# 자동 포스팅 규칙

매일 오전 9시(KST)에 예약 작업이 새 글 2개를 `_posts/`에 추가하고 커밋·push 합니다.

## 일본어 단어 글
- 파일명: `_posts/YYYY-MM-DD-japanese-vocab-dayN.md`
- front matter: `categories: [japanese]`, 제목 `일본어 단어 Day N`
- JLPT N2 수준 단어 30개를 표로 작성: 한자 | 히라가나 | 한글 뜻 | 예문 (예문 아래 한글 번역 포함)
- 이전 글(`japanese` 카테고리 전체)에 나온 단어는 다시 쓰지 않는다.

## CCNA 글
- 파일명: `_posts/YYYY-MM-DD-ccna-dayN.md`
- front matter: `categories: [ccna]`, 제목 `CCNA Day N: 주제`
- `automation/ccna_curriculum.md`의 다음 주제를 순서대로 작성 (20~30분 분량)
- 구성: 학습 목표, 핵심 개념, 예시나 명령어, 오늘의 일본어 IT 용어, 복습 퀴즈 5문제

## 공통
- 날짜 front matter는 `YYYY-MM-DD 09:00:00 +0900` 형식
- 커밋 메시지: `Add posts for YYYY-MM-DD`
