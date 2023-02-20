import 'dart:convert';

import 'package:app/models.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:socket_io_client/socket_io_client.dart';
import 'package:flutter/material.dart';

class SocketDataManager with ChangeNotifier {
  final IO.Socket socket;
  final GameAlreadyStarted _gameAlreadyStarted = GameAlreadyStarted();
  final GameNotFound _gameNotFound = GameNotFound();
  final UsernameAlreadyExists _usernameAlreadyExists = UsernameAlreadyExists();
  final StartGame _startGame = StartGame();
  final QuestionResults _questionResults = QuestionResults();
  final SetQuestionNumber _setQuestionNumber = SetQuestionNumber();
  final FinalResults _finalResults = FinalResults();
  final Solutions _solutions = Solutions();
  final Kick _kick = Kick();
  final JoinedGame _joinedGame = JoinedGame();

  SocketDataManager(String url, DataManager dataManager)
      : socket =
            IO.io(url, OptionBuilder().setTransports(['websocket']).build()) {
    socket.on('game_already_started', (data) {
      _gameAlreadyStarted.handleEvent(data);
      notifyListeners();
    });
    socket.on('game_not_found', (data) {
      _gameNotFound.handleEvent(data);
      notifyListeners();
    });
    socket.on('username_already_exists', (data) {
      _usernameAlreadyExists.handleEvent(data);
      notifyListeners();
    });
    socket.on("time_sync", (data) => {socket.emit("echo_time_sync", data)});
    socket.on('start_game', (data) {
      _startGame.handleEvent(data, dataManager);
      notifyListeners();
    });
    socket.on('question_results', (data) {
      _questionResults.handleEvent(data, dataManager);
      notifyListeners();
    });
    socket.on('set_question_number', (data) {
      debugPrint("set_question_number, $data");
      _setQuestionNumber.handleEvent(data, dataManager);
      notifyListeners();
    });
    socket.on('final_results', (data) {
      _finalResults.handleEvent(data);
      notifyListeners();
    });
    socket.on('solutions', (data) {
      _solutions.handleEvent(data, dataManager);
      notifyListeners();
    });
    socket.on('kick', (data) {
      _kick.handleEvent(data);
      notifyListeners();
    });
    socket.on("joined_game", (data) {
      _joinedGame.handleEvent(data, dataManager);
      notifyListeners();
    });
  }

  GameAlreadyStarted get gameAlreadyStarted => _gameAlreadyStarted;

  GameNotFound get gameNotFound => _gameNotFound;

  UsernameAlreadyExists get usernameAlreadyExists => _usernameAlreadyExists;

  StartGame get startGame => _startGame;

  QuestionResults get questionResults => _questionResults;

  SetQuestionNumber get setQuestionNumber => _setQuestionNumber;

  FinalResults get finalResults => _finalResults;

  Solutions get solutions => _solutions;

  Kick get kick => _kick;

  void joinGame(JoinGameSendData data) {
    socket.emit("join_game", data.toJson());
  }

  void submitAnswer(SubmitAnswerData data) {
    socket.emit("submit_answer", data.toJson());
  }
}

class GameAlreadyStarted {
  void handleEvent(dynamic data) {}
}

class GameNotFound {
  void handleEvent(dynamic data) {}
}

class UsernameAlreadyExists {
  void handleEvent(dynamic data) {}
}

class StartGame {
  void handleEvent(dynamic data, DataManager dm) {
    dm.gameData.value?.setStarted = true;
  }
}

class QuestionResults {
  late List<AnswerData> _data;

  List<AnswerData> get data => _data;

  void handleEvent(dynamic data, DataManager dm) {
    final json = jsonDecode(data) as List;
    _data = json.map((e) => AnswerData.fromJson(e)).toList().cast<AnswerData>();
    String? username = dm.username.value;
    for (var d in _data) {
      if (d.username == username) {
        dm.score.value += d.score;
        break;
      }
    }
    dm.answerData.value = _data;
  }
}

class SetQuestionNumber {
  late SetQuestionNumberData _data;

  SetQuestionNumberData get data => _data;

  void handleEvent(dynamic data, DataManager dm) {
    _data = SetQuestionNumberData.fromJson(data);
    dm.showSolutions.value = false;
    dm.answerData.value = null;
    dm.quizQuestion.value = _data.question;
    dm.gameData.value?.setCurrentQuestion = _data.qIndex;
  }
}

class FinalResults {
  // TODO
  String _data = "";

  String get data => _data;

  void handleEvent(dynamic data) {
    _data = data.toString();
  }
}

class Solutions {
  late QuizQuestion _data;

  QuizQuestion get data => _data;

  void handleEvent(dynamic data, DataManager dm) {
    _data = QuizQuestion.fromJson(jsonDecode(data));
    dm.showSolutions.value = true;
  }
}

class Kick {
  void handleEvent(dynamic data) {}
}

class JoinedGame {
  late JoinedGameData _data;

  JoinedGameData get data => _data;

  void handleEvent(dynamic data, DataManager dm) {
    _data = JoinedGameData.fromJson(data);
    dm.gameData.value = _data;
  }
}

class BasicStringEvent {
  String _data = "";

  String get data => _data;

  void handleEvent(dynamic data) {
    _data = data.toString();
  }
}

class DataManager extends ChangeNotifier {
  ValueNotifier<String?> username = ValueNotifier(null);
  ValueNotifier<JoinedGameData?> gameData = ValueNotifier(null);
  ValueNotifier<bool> showSolutions = ValueNotifier(false);
  ValueNotifier<List<AnswerData>?> answerData = ValueNotifier(null);
  ValueNotifier<int> score = ValueNotifier(0);
  ValueNotifier<GameQuizQuestion?> quizQuestion = ValueNotifier(null);
}
