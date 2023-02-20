import 'package:app/models.dart';
import 'package:app/play/questions/abcd.dart';
import 'package:app/play/wait_screen.dart';
import 'package:flutter/material.dart';

import '../baseGameScreen.dart';

class BaseQuestion extends StatefulWidget {
  const BaseQuestion({Key? key}) : super(key: key);

  @override
  State<BaseQuestion> createState() => _BaseQuestionState();
}

class _BaseQuestionState extends State<BaseQuestion> {
  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder(
        valueListenable: GameScreen.of(context).data.dataManager.gameData,
        builder: (ctx1, gd, child) {
          return ValueListenableBuilder(
              valueListenable: GameScreen.of(ctx1)
                  .data
                  .dataManager
                  .gameData
                  .value!
                  .currentQuestion,
              builder: (ctx2, qIndex, child) {
                if (qIndex == -1) {
                  return WaitScreen(
                      title: gd!.title, description: gd.description);
                } else {
                  return ValueListenableBuilder(
                      valueListenable:
                          GameScreen.of(ctx1).data.dataManager.answerData,
                      builder: (ctx2, ad, child) {
                        if (ad == null) {
                          return ShowQuestion();
                        } else {
                          return const Placeholder();
                        }
                      });
                }
              });
        });
  }
}

class ShowQuestion extends StatelessWidget {
  const ShowQuestion({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder(
        valueListenable: GameScreen.of(context).data.dataManager.quizQuestion,
        builder: (ctx, data, child) {
          switch (data?.type) {
            case QuizQuestionTypes.abcd:
              return AbcdQuestion(question: data!);
            case QuizQuestionTypes.range:
              return const Placeholder();
            case QuizQuestionTypes.voting:
              return const Placeholder();
            case QuizQuestionTypes.slide:
              return const Placeholder();
            case QuizQuestionTypes.text:
              return const Placeholder();
            case QuizQuestionTypes.order:
              return const Placeholder();
            case null:
              return const CircularProgressIndicator();
          }
        });
  }
}
