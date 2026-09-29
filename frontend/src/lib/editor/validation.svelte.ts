// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Whether the editor shows what is still missing (MVP.md D14). A new quiz is empty, so
// marking every empty field from the first render put red on the whole screen before the
// author had typed a word. The marks now wait for the first Save; after that they stay on,
// and update live as things get fixed.
//
// One flag for the whole editor rather than a prop threaded through the rail, the strip,
// the canvas and the header. The editor resets it when it opens.
//
// Over-length counters are not behind this: going over a limit is something the author
// just did, and saying so straight away is the useful moment.
export const editorValidation = $state({ shown: false });
