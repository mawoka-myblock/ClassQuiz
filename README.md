# ClassQuiz

ClassQuiz is a quiz-application like KAHOOT!, but open-source which is very important
if it is a product for educational purposes.
You can create quizzes and play them remotely with other people.
It is mainly made for teachers, who create a quiz, so students can compete with their knowledge against each other.

## Try it
There is a hosted version at [ClassQuiz.Mawoka.eu](https://classquiz.mawoka.eu?utm_medium=Github&utm_source=Readme).
It is not intended for real-life usage, although it should work.
The server is located in Karlsruhe, Germany and hosted by [netcup](https://mawoka.eu/redir?token=2).
If you want to use it in real-life,
please contact me on [my website](https://mawoka.eu/contact?utm_medium=Github&utm_source=Readme).
## Self-Host

Please see https://classquiz.mawoka.eu/docs/self-host

### Things to know about the structure
1. Everything depends on Redis (API and frontend).
2. The proxy-container is optional (Caddy), but makes your life easier
3. You need to set your reverse proxy up, so that it allows Socket.io-connections.

---
*Kahoot! and the K! logo are trademarks of Kahoot! AS*