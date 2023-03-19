import 'package:app/home.dart';
import 'package:dynamic_color/dynamic_color.dart';
import 'package:flutter/material.dart';

import 'color_scheme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return DynamicColorBuilder(builder: (light, dark) {
      return MaterialApp(
        title: 'ClassQuiz',
        theme: ThemeData(
          colorScheme: light ?? lightColorScheme,
          useMaterial3: true,
        ),
        darkTheme: ThemeData(
          colorScheme: dark ?? darkColorScheme,
          useMaterial3: true,
        ),
        themeMode: ThemeMode.dark,
        home: const HomeScreen(),
      );
    });
  }
}
