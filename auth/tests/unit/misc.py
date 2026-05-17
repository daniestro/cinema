from dataclasses import dataclass
from pathlib import Path

TESTPATH = Path(__file__).parent


@dataclass
class RSA:
    public: str
    private: str


def get_rsa() -> RSA:
    with open(TESTPATH / "test_data/rsa.private") as private:
        with open(TESTPATH / "test_data/rsa.pub") as public:
            return RSA(public=public.read(), private=private.read())
