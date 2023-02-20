import 'package:app/baseGameScreen.dart';
import 'package:app/models.dart';
import 'package:app/play/questions/abcd.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("ClassQuiz"),
      ),
      body: Column(
        children: const <Widget>[
          Center(
            child: JoinForm(),
          ),
          // Center(child: QrScanner())
        ],
      ),
    );
  }
}

class JoinForm extends StatefulWidget {
  const JoinForm({Key? key}) : super(key: key);

  @override
  State<JoinForm> createState() => _JoinFormState();
}

class _JoinFormState extends State<JoinForm> {
  final pinController = TextEditingController();
  final urlController = TextEditingController();

  @override
  void dispose() {
    pinController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    urlController.text = "http://192.168.2.243:8080";
    return Column(children: <Widget>[
      Padding(
          padding: const EdgeInsets.all(15),
          child: TextField(
            controller: urlController,
            decoration: const InputDecoration(labelText: "URL"),
          )),
      Padding(
          padding: const EdgeInsets.all(15),
          child: TextField(
            controller: pinController,
            keyboardType: TextInputType.number,
            textAlign: TextAlign.center,
            inputFormatters: <TextInputFormatter>[
              FilteringTextInputFormatter.digitsOnly
            ],
            decoration: const InputDecoration(labelText: "Game-PIN"),
            onChanged: (val) {
              if (val.length >= 6) {
                Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (ctx) => BaseGameScreen(
                            pin: int.parse(val), baseUrl: urlController.text)));
              }
            },
          )),
      Row(
        children: <Widget>[
          ElevatedButton(
              onPressed: () {
                Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (ctx) =>
                            const DebugScreen(qType: QuizQuestionTypes.abcd)));
              },
              child: const Text("Abcd"))
        ],
      )
    ]);
  }
}

class QrScanner extends StatefulWidget {
  const QrScanner({Key? key}) : super(key: key);

  @override
  State<QrScanner> createState() => _QrScannerState();
}

class _QrScannerState extends State<QrScanner> {
  @override
  Widget build(BuildContext context) {
    return MobileScanner(
        controller: MobileScannerController(
            facing: CameraFacing.back, torchEnabled: false, returnImage: false),
        onDetect: (cap) {
          final List<Barcode> barcodes = cap.barcodes;
          final Uint8List? image = cap.image;
          for (final barcode in barcodes) {
            debugPrint('Barcode found! ${barcode.rawValue}');
          }
        });
  }
}

class HexColor extends Color {
  static int _getColorFromHex(String hexColor) {
    hexColor = hexColor.toUpperCase().replaceAll("#", "");
    if (hexColor.length == 6) {
      hexColor = "FF$hexColor";
    }
    return int.parse(hexColor, radix: 16);
  }

  HexColor(final String hexColor) : super(_getColorFromHex(hexColor));
}

class DebugScreen extends StatelessWidget {
  final QuizQuestionTypes qType;

  const DebugScreen({Key? key, required this.qType}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        body: GameScreen(
            data: GameData(
                options: GameOptions(
                    captchaEnabled: false,
                    customField: null,
                    gameMode: "kahoot"),
                baseURL: "http://localhost:8080"),
            child: Builder(
              builder: (context) {
                switch (qType) {
                  case QuizQuestionTypes.abcd:
                    {
                      GameScreen.of(context).data.dataManager.gameData.value =
                          JoinedGameData(
                              description: "description",
                              title: "title",
                              gameId: "gameId",
                              gamePin: "gamePin",
                              started: true,
                              gameMode: "kahoot",
                              currentQuestion: 0,
                              questionCount: 1);
                      return AbcdQuestion(
                          question: GameQuizQuestion(
                              question: 'How old are you?',
                              time: 20.0,
                              answers: [
                                AbcdQuizAnswerWithoutSolution(answer: "answer 1"),
                                AbcdQuizAnswerWithoutSolution(answer: "answer 2", color: "#aa0000")
                              ],
                              type: QuizQuestionTypes.abcd,
                              image: null));
                    }
                  default:
                    return const Placeholder();
                }
              },
            )));
  }
}
