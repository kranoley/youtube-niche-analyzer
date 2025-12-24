import importlib.util
import os
import sys
import traceback


def discover_and_run(tests_dir="test"):
    base = os.path.abspath(os.path.dirname(__file__) + "/..")
    tests_path = os.path.join(base, tests_dir)
    if not os.path.isdir(tests_path):
        print("No tests directory found at", tests_path)
        return 0

    sys.path.insert(0, base)
    failures = 0

    for fname in sorted(os.listdir(tests_path)):
        if not fname.startswith("test_") or not fname.endswith(".py"):
            continue
        path = os.path.join(tests_path, fname)
        name = fname[:-3]
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"Running tests in {name}...")
        for attr in dir(module):
            if attr.startswith("test_") and callable(getattr(module, attr)):
                fn = getattr(module, attr)
                try:
                    fn()
                    print(f"  OK {attr}")
                except AssertionError:
                    failures += 1
                    print(f"  FAIL {attr} (AssertionError)")
                    traceback.print_exc()
                except Exception:
                    failures += 1
                    print(f"  ERROR {attr}")
                    traceback.print_exc()

    return failures


if __name__ == "__main__":
    fail = discover_and_run()
    if fail:
        print(f"{fail} test(s) failed")
        sys.exit(1)
    print("All tests passed")