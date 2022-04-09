<a href="https://github.com/mawoka-myblock/ClassQuiz/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/mawoka-myblock/classquiz?style=for-the-badge"></a>
<a href="https://github.com/mawoka-myblock/ClassQuiz/graphs/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/mawoka-myblock/classquiz?color=green&style=for-the-badge"></a>
<a href="https://github.com/mawoka-myblock/ClassQuiz/network/members"><img alt="GitHub forks" src="https://img.shields.io/github/forks/mawoka-myblock/classquiz?style=for-the-badge"></a>
<a href="https://github.com/mawoka-myblock/ClassQuiz/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc"><img alt="GitHub issues" src="https://img.shields.io/github/issues/mawoka-myblock/classquiz?style=for-the-badge"></a>
<a href="https://github.com/mawoka-myblock/ClassQuiz/blob/master/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/mawoka-myblock/classquiz?style=for-the-badge"></a>
<img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/mawoka-myblock/classquiz?style=for-the-badge">
[![DeepSource](https://deepsource.io/gh/mawoka-myblock/ClassQuiz.svg/?label=active+issues&show_trend=true&token=5-2Na9HN-2CXcGkHjah_Rk09&style=for-the-badge)](https://deepsource.io/gh/mawoka-myblock/ClassQuiz/)
<img alt="Snky badge" src="https://img.shields.io/badge/Snyk-Check-success?style=for-the-badge">

<div align='center'>
    <h2 align='center'>ClassQuiz</h2>
    <img src='logo.png' alt='ClassQuiz Logo' height='100px' width='100px'>
    <p align='center'>
        The open-source quiz-platform!
        <br/>
        <a href='https://classquiz.mawoka.eu/'><strong>Visit the website »</strong></a>
        <br />
        <br />
        <a href='https://classquiz.mawoka.eu/docs'>Docs</a>
        ·
        <a href='https://classquiz.mawoka.eu/account/register'>Register</a>
        ·
        <a href='https://classquiz.mawoka.eu/docs/self-host'>Self-Hosting</a>
    </p>
</div>

## About ClassQuiz

ClassQuiz is a quiz-application like KAHOOT!, but open-source which is very important if it is a product for educational
purposes. You can create quizzes and play them remotely with other people. It is mainly made for teachers, who create a
quiz, so students can compete with their knowledge against each other.

## Try it

There is a hosted version at [ClassQuiz.Mawoka.eu](https://classquiz.mawoka.eu?utm_medium=Github&utm_source=Readme). The
server is located in Karlsruhe, Germany and hosted by [netcup](https://mawoka.eu/redir?token=2), so expect some latency
depending on your location.

## Self-Host

Please see https://classquiz.mawoka.eu/docs/self-host

## Development

See https://classquiz.mawoka.eu/docs/develop

## Docs

The docs are online at https://classquiz.mawoka.eu/docs

### Things to know about the structure

1. Everything depends on Redis (API and frontend).
2. The proxy-container is optional (Caddy), but makes your life easier
3. You need to set your reverse proxy up, so that it allows Socket.io-connections.

---
*Kahoot! and the K! logo are trademarks of Kahoot! AS*