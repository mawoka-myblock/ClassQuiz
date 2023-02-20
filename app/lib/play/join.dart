import 'package:app/baseGameScreen.dart';
import 'package:app/models.dart';
import 'package:flutter/material.dart';


class JoinGame extends StatefulWidget {
  final String gamePin;
  const JoinGame({Key? key, required this.gamePin}) : super(key: key);

  @override
  State<JoinGame> createState() => _JoinGameState();
}

class _JoinGameState extends State<JoinGame> {
  final _formKey = GlobalKey<FormState>();
  final usernameKey = TextEditingController();
  final customFieldController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Builder(builder: (BuildContext innerContext) {
      List<Widget> children = [];
      children.add(TextFormField(
        controller: usernameKey,
        decoration: const InputDecoration(labelText: "Username"),
      ));
      if (GameScreen.of(innerContext).data.options.customField != null) {
        children.add(TextFormField(
          controller: customFieldController,
          decoration: InputDecoration(
              labelText: GameScreen.of(innerContext).data.options.customField),
        ));
      }
      children.add(ElevatedButton(
          onPressed: () {
            // if (usernameKey.text.length > 3 || usernameKey.text.length < 10) {
            //   return;
            // }
            debugPrint("ok!");
            setState(() {
              GameScreen.of(innerContext).data.socketDataManager.joinGame(JoinGameSendData(username: usernameKey.text, gamePin: widget.gamePin));
              GameScreen.of(innerContext).data.dataManager.username.value = usernameKey.text;
            });
          },
          child: const Text("Submit")));
      return Form(
          child: Column(
        children: children,
      ));
    });
  }
}
