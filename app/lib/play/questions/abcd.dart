import 'package:app/baseGameScreen.dart';
import 'package:app/home.dart';
import 'package:app/models.dart';
import 'package:circular_countdown_timer/circular_countdown_timer.dart';
import 'package:flutter/material.dart';

class AbcdQuestion extends StatefulWidget {
  final GameQuizQuestion question;

  const AbcdQuestion({Key? key, required this.question}) : super(key: key);

  @override
  State<AbcdQuestion> createState() => _AbcdQuestionState();
}

class _AbcdQuestionState extends State<AbcdQuestion> {
  final CountDownController _countDownController = CountDownController();

  @override
  Widget build(BuildContext context) {
    List<Widget> buttons = [];
    final int qIndex = GameScreen.of(context)
        .data
        .dataManager
        .gameData
        .value!
        .currentQuestion
        .value;
    for (AbcdQuizAnswerWithoutSolution answer in widget.question.answers) {
      Color? bgColor = HexColor(answer.color ?? '#fffff');
      buttons.add(Expanded(
          child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 5),
              child: ElevatedButton(
                onPressed: () {
                  GameScreen.of(context).data.socketDataManager.submitAnswer(
                      SubmitAnswerData(qIndex: qIndex, answer: answer.answer));
                },
                style: ButtonStyle(backgroundColor:
                    MaterialStateProperty.resolveWith<Color?>((states) {
                  if (states.contains(MaterialState.disabled)) {
                    return null;
                  }
                  return answer.color == null ? null : HexColor(answer.color!);
                })),
                child: Text(answer.answer),
              ))));
    }

    return Padding(
        padding: const EdgeInsets.all(10),
        child:
            Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
          Padding(
              padding: const EdgeInsets.symmetric(vertical: 5),
              child: CircularCountDownTimer(
                controller: _countDownController,
                width: MediaQuery.of(context).size.width,
                height: MediaQuery.of(context).size.height / 5,
                duration: widget.question.time.toInt(),
                fillColor: Colors.green,
                ringColor: Colors.greenAccent,
                isReverse: true,
                isReverseAnimation: true,
              )),
          ...buttons
        ]));
  }
}
