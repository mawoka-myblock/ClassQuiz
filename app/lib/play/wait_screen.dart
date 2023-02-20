import 'package:flutter/material.dart';

class WaitScreen extends StatelessWidget {
  final String title;
  final String description;

  const WaitScreen({Key? key, required this.title, required this.description})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: <Widget>[
        Text(title, style: const TextStyle(fontSize: 30)),
        Text(
          description,
        )
      ],
    );
  }
}
