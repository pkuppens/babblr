# Non-Functional Requirements

## Purpose

Specifies how well the system must perform.

## Performance

**NFR-P1**: Response time <3s (p90) for AI responses
**NFR-P2**: STT latency <5s
**NFR-P3**: TTS latency <2s

## Usability

**NFR-U1**: Intuitive UI requiring minimal documentation
**NFR-U2**: Clear error messages
**NFR-U3**: Keyboard navigation support

## Reliability

**NFR-R1**: Graceful degradation on LLM failures
**NFR-R2**: Data persistence (no data loss)
**NFR-R3**: Crash recovery

## Security

**NFR-S1**: Secure API key storage (environment variables)
**NFR-S2**: SQL injection protection (ORM)
**NFR-S3**: Dependency vulnerability scanning

## Scalability

**NFR-SC1**: Support 1000+ messages per conversation
**NFR-SC2**: Support 10,000+ words per language

## Compatibility

**NFR-C1**: Windows, macOS, Linux support

---

**Version**: 1.0.0
**Last Updated**: 2026-02-02
