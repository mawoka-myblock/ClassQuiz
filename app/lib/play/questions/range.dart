import 'package:app/baseGameScreen.dart';
import 'package:app/home.dart';
import 'package:app/models.dart';
import 'package:circular_countdown_timer/circular_countdown_timer.dart';
import 'package:flutter/material.dart';

class RangeQuestion extends StatefulWidget {
  final GameQuizQuestion question;

  const RangeQuestion({Key? key, required this.question}) : super(key: key);

  @override
  State<RangeQuestion> createState() => _RangeQuestionState();
}

class _RangeQuestionState extends State<RangeQuestion> {
  final CountDownController _countDownController = CountDownController();
  bool _answerSubmitted = false;
  double _currentSliderValue = 20;

  @override
  Widget build(BuildContext context) {
    final RangeQuizAnswerWithoutSolution answer = widget.question.answers;
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
                textStyle:
                    TextStyle(color: Theme.of(context).colorScheme.primary),
                isReverse: true,
                isReverseAnimation: true,
                onComplete: () {
                  setState(() {
                    _answerSubmitted = true;
                  });
                },
              )),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 5),
            child: Slider(
              value: _currentSliderValue,
              max: answer.max.toDouble(),
              min: answer.min.toDouble(),
              label: _currentSliderValue.round().toString(),
              onChanged: (double value) {
                setState(() {
                  _currentSliderValue = value;
                });
              },
            ),
          )
        ]));
  }
}
