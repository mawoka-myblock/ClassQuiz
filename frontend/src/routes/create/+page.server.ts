// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Open to everyone. Signed out, the quiz is saved without an account and this browser
// keeps its ownership secret. This used to need `?anon=true`, and without it sent you
// to the login page -- so My Quizzes' Create button walled off exactly the people the
// signed-out My Quizzes page is for. Old `?anon=true` links still work; it is ignored.
export async function load() {
	return {};
}
