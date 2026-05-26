# Changelog

## v3.0.0

### Security

- Password-based authentication with hashed credentials (replaces insecure URL parameter login)
- Brute-force protection: account lockout after 5 failed attempts in 15 minutes
- Rate limiting: 20 AI calls per 10 minutes, persisted in database across sessions
- Input sanitization: all user text stripped of HTML tags and javascript URIs (XSS prevention)
- API key display removed from Settings (only shows set/not-set status)

### Tone & Personality

- Complete rewrite of all AI prompts to sound warm, human, and conversational
- All UI copy updated to be inviting and supportive rather than clinical or robotic
- Empathy level control (1-10) lets users set how warm or direct the AI sounds
- 5 therapeutic chat modes: Open, CBT, Validation, Reflection, Check-in

### Integration & Context Sharing

- All modules now share context: goals, analysis results, chat history, and journal entries inform each other
- AI Deep Analysis feeds into AI Chat for continuity
- Dashboard check-in data influences skill recommendations and mood forecasts
- Onboarding preferences shape AI responses across the entire app

### New Features

- Daily emoji check-in with mood and energy tracking
- Streak system with 1-day grace period for recovery
- Sample data generation for new users to explore features immediately
- Contextual skill recommendations based on recent journal content
- PHQ-9 and GAD-7 structured mental health check-ins
- AI mood forecast and weekly narrative summaries
- 4 skill module categories (Mindfulness, Distress Tolerance, Self-Compassion, Cognitive Skills)
- 4 reflection journeys (Heartbreak, Motivation, Anxiety, Self-Worth)
- Quick grounding tools and guided breathing exercises
- Personalized onboarding wizard (4 steps)
- 5 journal templates including Thought Record CBT and Body Check-In
- Live cognitive distortion detection while writing
- Goal tracking with visual progress
- Backup and restore functionality
- Full data export (JSON + CSV)

### Bug Fixes

- Fixed `page_history` indentation causing render errors
- Fixed `goal_text` field name mismatch (renamed to `title`)
- Fixed streak calculation anchoring to today instead of floating
- Fixed UTC/local timezone mismatch in daily check-in detection
- Fixed retry button to re-send the last failed prompt instead of just rerunning the page
