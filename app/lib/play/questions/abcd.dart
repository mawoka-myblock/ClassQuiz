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
  bool _buttonsEnabled = true;

  Widget _getButton(int qIndex, AbcdQuizAnswerWithoutSolution answer) {
    return Expanded(
        child: Padding(
            padding: const EdgeInsets.all(2.5),
            child: ElevatedButton(
              onPressed: _buttonsEnabled
                  ? () {
                      GameScreen.of(context)
                          .data
                          .socketDataManager
                          .submitAnswer(SubmitAnswerData(
                              qIndex: qIndex, answer: answer.answer));
                      setState(() {
                        _buttonsEnabled = false;
                        _countDownController.reset();
                      });
                    }
                  : null,
              style: ButtonStyle(backgroundColor:
                  MaterialStateProperty.resolveWith<Color?>((states) {
                if (states.contains(MaterialState.disabled)) {
                  return null;
                }
                return answer.color == null ? null : HexColor(answer.color!);
              })),
              child: Text(answer.answer,
                  style: TextStyle(
                      color: answer.color == null || !_buttonsEnabled ? null : Colors.black)),
            )));
  }

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
    List<AbcdQuizAnswerWithoutSolution> answers = widget.question.answers;

/*    buttons.add(Expanded(
        child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 5),
            child: _getButton(qIndex, answers[0]))));*/
    buttons.add(Expanded(
        child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 2.5),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _getButton(qIndex, answers[0]),
                _getButton(qIndex, answers[1])
              ],
            ))));
    if (answers.length == 3) {
      buttons.add(Expanded(
          child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 2.5),
              child: _getButton(qIndex, answers[2]))));
    }
    if (answers.length == 4) {
      buttons.add(Expanded(
          child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 2.5),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _getButton(qIndex, answers[2]),
                  _getButton(qIndex, answers[3])
                ],
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
                fillColor: Theme.of(context).colorScheme.primary,
                ringColor: Theme.of(context).colorScheme.onPrimary,
                textStyle: TextStyle(color: Theme.of(context).colorScheme.primary),
                isReverse: true,
                isReverseAnimation: true,
                onComplete: () {
                  setState(() {
                    _buttonsEnabled = false;
                  });
                },
              )),
          ...buttons
        ]));
  }
}
