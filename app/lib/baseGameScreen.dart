import 'dart:convert';

import 'package:app/play/base_question.dart';
import 'package:app/play/join.dart';
import 'package:flutter/material.dart';
import 'dart:async';
import 'package:http/http.dart' as http;

import 'models.dart';

class BaseGameScreen extends StatefulWidget {
  final int pin;
  final String baseUrl;

  const BaseGameScreen({Key? key, required this.pin, required this.baseUrl})
      : super(key: key);

  @override
  State<BaseGameScreen> createState() => _BaseGameScreenState();
}

class _BaseGameScreenState extends State<BaseGameScreen> {
  Future<GameOptions> getGameOptions() async {
    final resp = await http.get(Uri.parse(
        "${widget.baseUrl}/api/v1/quiz/play/check_captcha/${widget.pin}"));
    final json = jsonDecode(resp.body);
    debugPrint("$json");
    return GameOptions.fromJson(json);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: FutureBuilder(
          future: getGameOptions(),
          builder: (BuildContext context, AsyncSnapshot<GameOptions> snapshot) {
            if (snapshot.hasData) {
              return GameScreen(
                  data: GameData(
                      options: snapshot.requireData, baseURL: widget.baseUrl),
                  child: Builder(
                    builder: (BuildContext innerContext) {
                      return ValueListenableBuilder(
                          valueListenable: GameScreen.of(innerContext)
                              .data
                              .dataManager
                              .gameData,
                          builder: (ctx, gameData, child) {
                            if (gameData != null) {
                              return const BaseQuestion();
                            } else {
                              return JoinGame(gamePin: widget.pin.toString());
                            }
                          });
                    },
                  ));
            } else {
              return const CircularProgressIndicator();
            }
          }),
    );
  }
}

class GameScreen extends InheritedWidget {
  const GameScreen({
    Key? key,
    required Widget child,
    required this.data,
  }) : super(key: key, child: child);

  final GameData data;

  static GameScreen of(BuildContext context) {
    final GameScreen? result =
        context.dependOnInheritedWidgetOfExactType<GameScreen>();
    assert(result != null, 'No GameScreen found in context');
    return result!;
  }

  @override
  bool updateShouldNotify(GameScreen old) {
    return data != old.data;
  }
}
