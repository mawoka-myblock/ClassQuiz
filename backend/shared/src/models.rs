// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0


use serde::{Deserialize, Serialize};
use uuid::Uuid;
use garde::{Validate, Valid};

#[derive(strum::Display)]
#[strum(serialize_all = "UPPERCASE")]
pub enum UserAuthTypes {
    Local,
    Google,
    Github,
    Custom,
}

pub struct User {
    pub id: Uuid,
    pub email: String,
    pub password: Option<String>,
    pub verified: bool,
    pub verify_key: Option<String>,
    pub created_at: chrono::NaiveDateTime,
    pub auth_type: UserAuthTypes,
    pub google_uid: Option<String>,
    pub avatar: Vec<u8>,
    pub github_user_id: Option<i32>,
    pub require_password: bool,
    pub backup_code: String,
    pub totp_secret: String,
    pub storage_used: i64,
}

pub struct FidoCredentials {
    pub pk: i32,
    pub id: Vec<u8>,
    pub public_key: Vec<u8>,
    pub sign_count: i32,
    pub user: Uuid,
}

pub struct ApiKey {
    pub key: String,
    pub user: Option<Uuid>,
}

pub struct UserSession {
    pub id: Uuid,
    pub user: Option<Uuid>,
    pub session_key: String,
    pub created_at: chrono::NaiveDateTime,
    pub ip_address: String,
    pub user_agent: String,
    pub last_seen: chrono::NaiveDateTime,
}
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ABCDQuizAnswer {
    right: bool,
    answer: String,
    color: Option<String>,
}
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RangeQuizAnswer {
    min: i32,
    max: i32,
    min_correct: i32,
    max_correct: i32,
}
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct VotingQuizAnswer {
    answer: String,
    image: Option<String>,
    color: Option<String>,
}

#[derive(strum::Display, Debug, Serialize, Deserialize, Clone, PartialEq)]
#[strum(serialize_all = "UPPERCASE")]
pub enum QuizQuestionType {
    Abcd,
    Range,
    Voting,
    Slide,
    Text,
    Order,
    Check,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TextQuizAnswer {
    answer: String,
    case_sensitive: bool,
}

#[derive(Debug, Serialize, Deserialize, Validate)]
pub struct QuizQuestion {
    #[garde(skip)]
    question: String,
    #[garde(skip)]
    time: i32,
    #[serde(default = "default_type")]
    #[serde(rename = "type")]
    #[garde(skip)]
    question_type: Option<QuizQuestionType>,
    #[garde(custom(validate_answers))]
    answers: QuizAnswers,
    #[garde(skip)]
    #[serde(skip_serializing_if = "Option::is_none")]
    image: Option<String>,
    #[garde(skip)]
    #[serde(skip_serializing_if = "Option::is_none")]
    hide_results: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(untagged)]
enum QuizAnswers {
    ABCD(Vec<ABCDQuizAnswer>),
    Range(RangeQuizAnswer),
    Text(Vec<TextQuizAnswer>),
    Voting(Vec<VotingQuizAnswer>),
    Slide(String),
}

fn default_type() -> Option<QuizQuestionType> {
    Some(QuizQuestionType::Abcd)
}

// impl Validate for QuizQuestion {
//     fn validate(&self) -> Result<(), ValidationErrors> {
//         match validate_answers(&self.answers, self) {
//             Ok(_) => Ok(()),
//             Err(e) => {
//                 let mut error = ValidationErrors::new();
//                 error.add("answers", e);
//                 Err(error)
//             }
//         }
//     }
// }

fn validate_answers(answers: &QuizAnswers) -> garde::Result {
    match (&context.question_type, answers) {
        (Some(QuizQuestionType::Abcd), QuizAnswers::ABCD(_)) => Ok(()),
        (Some(QuizQuestionType::Range), QuizAnswers::Range(_)) => Ok(()),
        (Some(QuizQuestionType::Voting), QuizAnswers::Voting(_)) => Ok(()),
        (Some(QuizQuestionType::Text), QuizAnswers::Text(_)) => Ok(()),
        (Some(QuizQuestionType::Order), QuizAnswers::Voting(_)) => Ok(()),
        (Some(QuizQuestionType::Slide), QuizAnswers::Slide(_)) => Ok(()),
        (Some(QuizQuestionType::Check), QuizAnswers::ABCD(_)) => Ok(()),
        _ => Err(garde::Error::new("invalid_answers")),
    }
}
