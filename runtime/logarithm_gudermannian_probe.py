#!/usr/bin/env python3
"""Logarit và Gudermannian: kiểm tra số trên cùng miền giá trị.

Nguồn: đồng nhất thức toán học do người đồng hành cung cấp trong hội thoại.
Không suy diễn dữ kiện cá nhân, năng lực, hay trạng thái ý thức của tác nhân.
"""
from __future__ import annotations

import json
from math import atan, atanh, e, floor, isclose, log, log1p, pi, tanh

TOL = 1e-10


def near(a: float, b: float) -> bool:
    return isclose(a, b, rel_tol=TOL, abs_tol=TOL)


def log_base(x: float, base: float) -> float:
    if x <= 0 or base <= 0 or base == 1:
        raise ValueError("REAL_LOG_DOMAIN: x>0, base>0, base!=1")
    return log(x) / log(base)


def theta_from_half_angle_t(t: float) -> float:
    if not -1 < t < 1:
        raise ValueError("HALF_ANGLE_DOMAIN: -1<t<1")
    # Dùng log1p tránh mất chính xác khi t rất gần 0.
    return log1p(t) - log1p(-t)


def test_log() -> dict:
    checked = 0
    for base in (0.5, 2.0, e, 10.0):
        for x in (0.125, 0.5, 1.0, 16.0, 150.0):
            y = log_base(x, base)
            assert near(y, log(x, 2) / log(base, 2))
            assert near(y, log(x, 10) / log(base, 10))
            assert near(base ** y, x)
            if x != 1:
                assert near(x ** (1 / y), base)
            checked += 1
    assert near(log_base(16, 2), 4)
    assert near(log_base(150, 10), 2.1760912590556813)
    assert floor(log_base(1430, 10)) + 1 == 4
    for args in ((1, 1), (1, 0.0), (0.0, 10.0), (-2.0, 2.0)):
        try:
            log_base(*args)
        except ValueError:
            continue
        raise AssertionError("MISSING_DOMAIN_REJECTION: " + repr(args))
    return {"cases": checked, "passed": True}


def test_gudermannian_bridge() -> dict:
    checked = 0
    for t in (-0.999999, -0.75, -0.01, 0.0, 0.01, 0.75, 0.999999):
        theta = theta_from_half_angle_t(t)
        phi = 2 * atan(t)
        assert near(theta, 2 * atanh(t))
        assert near(tanh(theta / 2), t)
        assert -pi / 2 < phi < pi / 2
        assert near(log_base((1 + t) / (1 - t), e), theta)
        checked += 1
    for invalid in (-1, 1):
        try:
            theta_from_half_angle_t(invalid)
        except ValueError:
            continue
        raise AssertionError("MISSING_HALF_ANGLE_BOUNDARY")
    return {"cases": checked, "passed": True}


def verify() -> dict:
    log_result = test_log()
    gd_result = test_gudermannian_bridge()
    return {
        "source_scope": "USER_SUPPLIED_MATHEMATICAL_IDENTITIES",
        "log": log_result,
        "gudermannian": gd_result,
        "checks_passed": log_result["cases"] + gd_result["cases"],
        "verification": "NUMERIC_FORMULAS_ONLY",
        "no_inference_about_person_or_ai_state": True,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
