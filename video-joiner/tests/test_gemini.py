import base64, json, os, tempfile, unittest, wave
from unittest import mock
from videojoiner import gemini


def fake_resp(obj):
    m = mock.MagicMock()
    m.__enter__.return_value = m
    m.read.return_value = json.dumps(obj).encode()
    return m


class GeminiTest(unittest.TestCase):
    def test_srt_format(self):
        srt = gemini.segments_to_srt([{"start": 0, "end": 1.5, "text": "สวัสดี"},
                                      {"start": 3661.25, "end": 3662, "text": "b"}])
        self.assertIn("1\n00:00:00,000 --> 00:00:01,500\nสวัสดี", srt)
        self.assertIn("2\n01:01:01,250 --> 01:01:02,000\nb", srt)

    def test_missing_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(gemini.GeminiError):
                gemini._call("m", {})

    def test_tts_writes_valid_wav(self):
        pcm = b"\x00\x01" * 2400
        resp = {"candidates": [{"content": {"parts": [{"inlineData": {
            "data": base64.b64encode(pcm).decode()}}]}}]}
        with tempfile.TemporaryDirectory() as d, \
             mock.patch.dict(os.environ, {"GEMINI_API_KEY": "x"}), \
             mock.patch("urllib.request.urlopen", return_value=fake_resp(resp)):
            out = gemini.synthesize_speech("hi", os.path.join(d, "v.wav"))
            with wave.open(str(out)) as w:
                self.assertEqual((w.getnchannels(), w.getframerate(), w.getnframes()), (1, 24000, 2400))

    def test_transcribe_payload_has_audio(self):
        p = gemini.build_transcribe_payload(b"abc")
        self.assertEqual(p["contents"][0]["parts"][1]["inline_data"]["data"], "YWJj")


if __name__ == "__main__":
    unittest.main()
