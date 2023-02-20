import 'dart:async';
import 'dart:ffi';
import 'package:app/play/listeners.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:socket_io_client/socket_io_client.dart';
import 'package:flutter/material.dart';

class GameOptions {
  final bool captchaEnabled;
  final String gameMode;
  final String? customField;

  GameOptions(
      {required this.captchaEnabled,
      required this.gameMode,
      required this.customField});

  factory GameOptions.fromJson(Map<String, dynamic> json) {
    return GameOptions(
        captchaEnabled: json["enabled"],
        gameMode: json["game_mode"],
        customField: json["custom_field"]);
  }
}

class GameData {
  final GameOptions options;
  final String baseURL;
  DataManager dataManager = DataManager();
  late SocketDataManager socketDataManager;

  GameData({required this.options, required this.baseURL}) {
    socketDataManager = SocketDataManager(baseURL, dataManager);
  }
}

class AnswerData {
  final String username;
  final String answer;
  final bool right;
  final double timeTaken;
  final int score;

  AnswerData(
      {required this.username,
      required this.answer,
      required this.right,
      required this.timeTaken,
      required this.score});

  factory AnswerData.fromJson(Map<String, dynamic> json) {
    return AnswerData(
        username: json["username"],
        answer: json["answer"],
        right: json["right"],
        timeTaken: json["time_taken"],
        score: json["score"]);
  }
}

class SetQuestionNumberData {
  final int qIndex;
  final GameQuizQuestion question;

  SetQuestionNumberData({required this.qIndex, required this.question});

  factory SetQuestionNumberData.fromJson(Map<String, dynamic> json) {
    return SetQuestionNumberData(
        qIndex: json["question_index"],
        question: GameQuizQuestion.fromJson(json["question"]));
  }
}

class AbcdQuizAnswerWithoutSolution {
  final String answer;
  final String? color;

  AbcdQuizAnswerWithoutSolution({required this.answer, this.color});

  factory AbcdQuizAnswerWithoutSolution.fromJson(Map<String, dynamic> json) {
    return AbcdQuizAnswerWithoutSolution(
        answer: json["answer"], color: json["color"]);
  }
}

class RangeQuizAnswerWithoutSolution {
  final int min;
  final int max;

  RangeQuizAnswerWithoutSolution({required this.min, required this.max});

  factory RangeQuizAnswerWithoutSolution.fromJson(Map<String, dynamic> json) {
    return RangeQuizAnswerWithoutSolution(min: json["min"], max: json["max"]);
  }
}

dynamic parseGameQuizQuestionAnswers(
    QuizQuestionTypes type, dynamic answersJson) {
  switch (type) {
    case QuizQuestionTypes.abcd:
      return List<AbcdQuizAnswerWithoutSolution>.from(answersJson.map(
          (answerJson) => AbcdQuizAnswerWithoutSolution.fromJson(answerJson)));
    case QuizQuestionTypes.range:
      return RangeQuizAnswerWithoutSolution.fromJson(answersJson);
    case QuizQuestionTypes.voting:
      return List<VotingQuizAnswer>.from(answersJson
          .map((answerJson) => VotingQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.text:
      return List<TextQuizAnswer>.from(
          answersJson.map((answerJson) => TextQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.order:
      return List<VotingQuizAnswer>.from(answersJson
          .map((answerJson) => VotingQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.slide:
      return answersJson.toString();
    default:
      return answersJson;
  }
}

class GameQuizQuestion extends QuizQuestion {
  GameQuizQuestion(
      {required super.question,
      required super.time,
      required super.type,
      required super.answers,
      required super.image}) {
    validateAnswers();
  }

  @override
  dynamic validateAnswers() {
    debugPrint("$answers");
    if (type == QuizQuestionTypes.abcd &&
        answers is! List<AbcdQuizAnswerWithoutSolution>) {
      throw Exception("Answers can't be null if type is ABCD");
    }
    if (type == QuizQuestionTypes.range &&
        answers is! RangeQuizAnswerWithoutSolution) {
      throw Exception(
          "Answer must be from type RangeQuizAnswer if type is RANGE");
    }
    if (type == QuizQuestionTypes.voting &&
        answers is! List<VotingQuizAnswer>) {
      throw Exception(
          "Answer must be from type VotingQuizAnswer if type is VOTING");
    }
    return answers;
  }

  factory GameQuizQuestion.fromJson(Map<String, dynamic> json) {
    return GameQuizQuestion(
        question: json["question"],
        time: double.parse(json["time"]),
        type: quizQuestionTypeFromString(json["type"]),
        answers: parseGameQuizQuestionAnswers(
            quizQuestionTypeFromString(json["type"]), json["answers"]),
        image: json["image"]);
  }
}

class JoinedGameData {
  final String description;
  final String title;
  final String gameId;
  final String gamePin;
  ValueNotifier<bool> started;
  final String? coverImage;
  final String gameMode;
  ValueNotifier<int> currentQuestion;
  final String? backgroundColor;
  final String? backgroundImage;
  final String? customField;
  final int questionCount;

  JoinedGameData(
      {required this.description,
      required this.title,
      required this.gameId,
      required this.gamePin,
      required bool started,
      this.coverImage,
      required this.gameMode,
      required int currentQuestion,
      this.backgroundColor,
      this.backgroundImage,
      this.customField,
      required this.questionCount})
      : started = ValueNotifier<bool>(started),
        currentQuestion = ValueNotifier<int>(currentQuestion);

  factory JoinedGameData.fromJson(Map<String, dynamic> json) {
    return JoinedGameData(
        description: json["description"],
        title: json["title"],
        gameId: json["game_id"],
        gamePin: json["game_pin"],
        started: json["started"],
        coverImage: json["cover_image"],
        gameMode: json["game_mode"],
        currentQuestion: json["current_question"],
        backgroundColor: json["background_color"],
        backgroundImage: json["background_image"],
        customField: json["custom_field"],
        questionCount: json["question_count"]);
  }

  set setStarted(bool val) {
    started.value = val;
  }

  set setCurrentQuestion(int val) {
    currentQuestion.value = val;
  }
}

enum QuizQuestionTypes { abcd, range, voting, slide, text, order }

QuizQuestionTypes quizQuestionTypeFromString(String typeString) {
  switch (typeString) {
    case 'ABCD':
      return QuizQuestionTypes.abcd;
    case 'RANGE':
      return QuizQuestionTypes.range;
    case 'VOTING':
      return QuizQuestionTypes.voting;
    case 'TEXT':
      return QuizQuestionTypes.text;
    case 'ORDER':
      return QuizQuestionTypes.order;
    case 'SLIDE':
      return QuizQuestionTypes.slide;
    default:
      throw Exception('Invalid quiz question type: $typeString');
  }
}

dynamic parseAnswers(QuizQuestionTypes type, dynamic answersJson) {
  switch (type) {
    case QuizQuestionTypes.abcd:
      return List<AbcdQuizAnswer>.from(
          answersJson.map((answerJson) => AbcdQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.range:
      return RangeQuizAnswer.fromJson(answersJson);
    case QuizQuestionTypes.voting:
      return List<VotingQuizAnswer>.from(answersJson
          .map((answerJson) => VotingQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.text:
      return List<TextQuizAnswer>.from(
          answersJson.map((answerJson) => TextQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.order:
      return List<VotingQuizAnswer>.from(answersJson
          .map((answerJson) => VotingQuizAnswer.fromJson(answerJson)));
    case QuizQuestionTypes.slide:
      return answersJson.toString();
    default:
      return answersJson;
  }
}

class QuizQuestion {
  final String question;
  final double time;
  QuizQuestionTypes type = QuizQuestionTypes.abcd;

  final dynamic answers;
  final String? image;

  QuizQuestion(
      {required this.question,
      required this.time,
      required this.type,
      required this.answers,
      required this.image}) {
    validateAnswers();
  }

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    return QuizQuestion(
        question: json["question"],
        time: json["time"],
        type: quizQuestionTypeFromString(json["type"]),
        answers: parseAnswers(
            quizQuestionTypeFromString(json["type"]), json["answers"]),
        image: json["image"]);
  }

  dynamic validateAnswers() {
    if (type == QuizQuestionTypes.abcd && answers is! List<AbcdQuizAnswer>) {
      throw Exception("Answers can't be null if type is ABCD");
    }
    if (type == QuizQuestionTypes.range && answers is! RangeQuizAnswer) {
      throw Exception(
          "Answer must be from type RangeQuizAnswer if type is RANGE");
    }
    if (type == QuizQuestionTypes.voting &&
        answers is! List<VotingQuizAnswer>) {
      throw Exception(
          "Answer must be from type VotingQuizAnswer if type is VOTING");
    }
    if (type == QuizQuestionTypes.text && answers is! List<TextQuizAnswer>) {
      throw Exception(
          "Answer must be from type TextQuizAnswer if type is TEXT");
    }
    if (type == QuizQuestionTypes.order && answers is! List<VotingQuizAnswer>) {
      throw Exception(
          "Answer must be from type VotingQuizAnswer if type is ORDER");
    }
    if (type == QuizQuestionTypes.slide && answers is! String) {
      throw Exception("Answer must be from type SlideElement if type is SLIDE");
    }
    return answers;
  }
}

class AbcdQuizAnswer {
  final bool right;
  final String answer;
  final String? color;

  AbcdQuizAnswer({required this.right, required this.answer, this.color});

  factory AbcdQuizAnswer.fromJson(Map<String, dynamic> json) {
    return AbcdQuizAnswer(right: json["right"], answer: json["answer"]);
  }
}

class RangeQuizAnswer {
  final int min;
  final int max;
  final int minCorrect;
  final int maxCorrect;

  RangeQuizAnswer(
      {required this.min,
      required this.max,
      required this.minCorrect,
      required this.maxCorrect});

  factory RangeQuizAnswer.fromJson(Map<String, dynamic> json) {
    return RangeQuizAnswer(
        min: json["min"],
        max: json["max"],
        minCorrect: json["min_correct"],
        maxCorrect: json["max_correct"]);
  }
}

class VotingQuizAnswer {
  final String answer;
  final String? image;
  final String? color;

  VotingQuizAnswer({required this.answer, this.image, this.color});

  factory VotingQuizAnswer.fromJson(Map<String, dynamic> json) {
    return VotingQuizAnswer(
        answer: json["answer"], color: json["color"], image: json["image"]);
  }
}

class TextQuizAnswer {
  final String answer;
  final bool caseSensitive;

  TextQuizAnswer({required this.answer, required this.caseSensitive});

  factory TextQuizAnswer.fromJson(Map<String, dynamic> json) {
    return TextQuizAnswer(
        answer: json["answer"], caseSensitive: json["case_sensitive"]);
  }
}

class JoinGameSendData {
  final String username;
  final String gamePin;
  final String? captcha;
  final String? customField;

  JoinGameSendData(
      {required this.username,
      required this.gamePin,
      this.captcha,
      this.customField});

  Map<String, dynamic> toJson() => {
        'username': username,
        'game_pin': gamePin,
        'captcha': captcha,
        'custom_field': customField
      };
}

class SubmitAnswerDataOrderType {
  final String answer;

  SubmitAnswerDataOrderType({required this.answer});

  Map<String, dynamic> toJson() {
    return {"answer": answer};
  }
}

class SubmitAnswerData {
  final int qIndex;
  final String answer;
  final List<SubmitAnswerDataOrderType>? complexAnswer;

  SubmitAnswerData(
      {required this.qIndex, required this.answer, this.complexAnswer});

  Map<String, dynamic> toJson() {
    return {
      "question_index": qIndex,
      "answer": answer,
      "complex_answer": complexAnswer?.map((e) => e.toJson()).toList(),
    };
  }
}
