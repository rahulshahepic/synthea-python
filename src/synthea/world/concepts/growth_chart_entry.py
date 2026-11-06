"""Java: org.mitre.synthea.world.concepts.GrowthChartEntry."""

from __future__ import annotations

import base64 as _pow_base64
import math
import math as _pow_math
import struct as _pow_struct
import zlib as _pow_zlib
from typing import ClassVar, cast

from synthea.world.concepts.growth_chart import GrowthChart


class GrowthChartEntry:
    """Java: GrowthChartEntry."""

    MAX_PERCENTILE: ClassVar[float] = 0.995

    def __init__(self, l: float, m: float, s: float) -> None:  # noqa: E741
        """Java: GrowthChartEntry#GrowthChartEntry."""
        self.lbox_cox: float = l
        self.median: float = m
        self.scov: float = s

    def zscore_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#zscoreForValue."""
        if self.lbox_cox == 0:
            return math.log(value / self.median) / self.scov
        return (_java_pow(value / self.median, self.lbox_cox) - 1) / (self.lbox_cox * self.scov)

    def percentile_for_value(self, value: float) -> float:
        """Java: GrowthChartEntry#percentileForValue."""
        return GrowthChart.zscore_to_percentile(self.zscore_for_value(value))

    def look_up(self, percentile: float) -> float:
        """Java: GrowthChartEntry#lookUp."""
        percentile_to_use = self.MAX_PERCENTILE if percentile > self.MAX_PERCENTILE else percentile
        z = GrowthChart.calculate_z_score(percentile_to_use)
        if self.lbox_cox == 0:
            return self.median * math.exp(self.scov * z)
        expression_term = self.lbox_cox * self.scov * z
        return self.median * _java_pow(1 + expression_term, 1.0 / self.lbox_cox)


# /*
# * Copyright (c) 2016, 2021, Intel Corporation. All rights reserved.
# * Copyright (C) 2021, Tencent. All rights reserved.
# * Intel Math Library (LIBM) Source Code
# *
# * DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER.
# *
# * This code is free software; you can redistribute it and/or modify it
# * under the terms of the GNU General Public License version 2 only, as
# * published by the Free Software Foundation.
# *
# * This code is distributed in the hope that it will be useful, but WITHOUT
# * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# * version 2 for more details (a copy is included in the LICENSE file that
# * accompanied this code).
# *
# * You should have received a copy of the GNU General Public License version
# * 2 along with this work; if not, write to the Free Software Foundation,
# * Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA.
# *
# * Please contact Oracle, 500 Oracle Parkway, Redwood Shores, CA 94065 USA
# * or visit www.oracle.com if you need additional information or have any
# * questions.
# *
# */
#
# Primary source: https://github.com/openjdk/jdk21u/blob/jdk-21.0.13%2B9/src/hotspot/cpu/x86/stubGenerator_x86_64_pow.cpp
# SHA-256: a166d4ff97a37e7d9c46519b541a159ca91bd642e046ca32a16f400197dc2a35

type _PowMemory = tuple[str, int | str, int | str, int, int]
type _PowArg = int | str | _PowMemory
_POW_OPS: tuple[tuple[str, tuple[_PowArg, ...]], ...] = (
    ("subq", ("rsp", 40)),
    ("movsd", (("m", "rsp", 0, 1, 8), "xmm0")),
    ("movsd", (("m", "rsp", 0, 1, 16), "xmm1")),
    ("movdq", ("r8", "xmm1")),
    ("cmp64", ("r8", ("m", 78096, 0, 1, 0), "r9")),
    ("jccb", ("notEqual", 8)),
    ("mulsd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("cmp64", ("r8", ("m", 78128, 0, 1, 0), "r9")),
    ("jccb", ("notEqual", 15)),
    ("movdq", ("r9", "xmm0")),
    ("cmp64", ("r9", ("m", 78112, 0, 1, 0), "r10")),
    ("jccb", ("less", 15)),
    ("sqrtsd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("pextrw", ("rax", "xmm0", 3)),
    ("xorpd", ("xmm2", "xmm2")),
    ("mov64", ("r9", 4607182418800017408)),
    ("movdq", ("xmm2", "r9")),
    ("movl", ("r8", 1069088768)),
    ("movdq", ("xmm7", "r8")),
    ("xorpd", ("xmm1", "xmm1")),
    ("mov64", ("r10", 8642407684923981824)),
    ("movdq", ("xmm1", "r10")),
    ("movdqu", ("xmm3", "xmm0")),
    ("movl", ("rdx", 32752)),
    ("andl", ("rdx", "rax")),
    ("subl", ("rdx", 16368)),
    ("movl", ("rcx", "rdx")),
    ("sarl", ("rdx", 31)),
    ("addl", ("rcx", "rdx")),
    ("xorl", ("rcx", "rdx")),
    ("por", ("xmm0", "xmm2")),
    ("movdqu", ("xmm6", ("m", 65536, 0, 1, 0), "r9")),
    ("psrlq", ("xmm0", 27)),
    ("movq", ("xmm2", ("m", 65552, 0, 1, 0), "r9")),
    ("psrld", ("xmm0", 2)),
    ("addl", ("rcx", 16)),
    ("bsrl", ("rcx", "rcx")),
    ("rcpps", ("xmm0", "xmm0")),
    ("psllq", ("xmm3", 12)),
    ("movl", ("r11", 8192)),
    ("movdq", ("xmm4", "r11")),
    ("psrlq", ("xmm3", 12)),
    ("subl", ("rax", 16)),
    ("cmpl", ("rax", 32736)),
    ("jcc", ("aboveEqual", 162)),
    ("movl", ("r8", 0)),
    ("mulss", ("xmm0", "xmm7")),
    ("movl", ("rdx", -1)),
    ("subl", ("rcx", 4)),
    ("shll", ("rdx",)),
    ("shlq", ("rdx", 32)),
    ("movdq", ("xmm5", "rdx")),
    ("por", ("xmm3", "xmm1")),
    ("subl", ("rax", 16351)),
    ("cmpl", ("rax", 1)),
    ("jcc", ("belowEqual", 719)),
    ("paddd", ("xmm0", "xmm4")),
    ("pand", ("xmm5", "xmm3")),
    ("movdl", ("rdx", "xmm0")),
    ("psllq", ("xmm0", 29)),
    ("subsd", ("xmm3", "xmm5")),
    ("pand", ("xmm0", "xmm6")),
    ("subl", ("rax", 1)),
    ("sarl", ("rax", 4)),
    ("cvtsi2sdl", ("xmm7", "rax")),
    ("mulpd", ("xmm5", "xmm0")),
    ("mulsd", ("xmm3", "xmm0")),
    ("movdqu", ("xmm1", ("m", 69776, 0, 1, 0), "r9")),
    ("lea", ("r11", 69872)),
    ("subsd", ("xmm5", "xmm2")),
    ("movdqu", ("xmm4", ("m", 69792, 0, 1, 0), "r9")),
    ("movl", ("rcx", "rax")),
    ("sarl", ("rax", 31)),
    ("addl", ("rcx", "rax")),
    ("xorl", ("rax", "rcx")),
    ("addl", ("rax", 1)),
    ("bsrl", ("rax", "rax")),
    ("unpcklpd", ("xmm5", "xmm3")),
    ("movdqu", ("xmm6", ("m", 69808, 0, 1, 0), "r9")),
    ("addsd", ("xmm3", "xmm5")),
    ("andl", ("rdx", 16760832)),
    ("shrl", ("rdx", 10)),
    ("addpd", ("xmm5", ("m", "r11", "rdx", 1, -3648))),
    ("movdqu", ("xmm0", ("m", 69824, 0, 1, 0), "r9")),
    ("pshufd", ("xmm2", "xmm3", 68)),
    ("mulsd", ("xmm3", "xmm3")),
    ("mulpd", ("xmm1", "xmm2")),
    ("mulpd", ("xmm4", "xmm2")),
    ("addsd", ("xmm5", "xmm7")),
    ("mulsd", ("xmm2", "xmm3")),
    ("addpd", ("xmm6", "xmm1")),
    ("mulsd", ("xmm3", "xmm3")),
    ("addpd", ("xmm0", "xmm4")),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movw", ("rcx", ("m", "rsp", 0, 1, 22))),
    ("pshufd", ("xmm7", "xmm5", 238)),
    ("movq", ("xmm4", ("m", 65568, 0, 1, 0), "r9")),
    ("mulpd", ("xmm6", "xmm2")),
    ("pshufd", ("xmm3", "xmm3", 68)),
    ("mulpd", ("xmm0", "xmm2")),
    ("shll", ("rax", 4)),
    ("subl", ("rax", 15872)),
    ("andl", ("rcx", 32752)),
    ("addl", ("rax", "rcx")),
    ("mulpd", ("xmm3", "xmm6")),
    ("cmpl", ("rax", 624)),
    ("jcc", ("aboveEqual", 257)),
    ("xorpd", ("xmm6", "xmm6")),
    ("movl", ("rdx", 17080)),
    ("pinsrw", ("xmm6", "rdx", 3)),
    ("movdqu", ("xmm2", "xmm1")),
    ("pand", ("xmm4", "xmm1")),
    ("subsd", ("xmm1", "xmm4")),
    ("mulsd", ("xmm4", "xmm5")),
    ("addsd", ("xmm0", "xmm7")),
    ("mulsd", ("xmm1", "xmm5")),
    ("movdqu", ("xmm7", "xmm6")),
    ("addsd", ("xmm6", "xmm4")),
    ("lea", ("r11", 65584)),
    ("addpd", ("xmm3", "xmm0")),
    ("movdl", ("rdx", "xmm6")),
    ("subsd", ("xmm6", "xmm7")),
    ("pshufd", ("xmm0", "xmm3", 238)),
    ("subsd", ("xmm4", "xmm6")),
    ("addsd", ("xmm0", "xmm3")),
    ("movl", ("rcx", "rdx")),
    ("andl", ("rdx", 255)),
    ("addl", ("rdx", "rdx")),
    ("movdqu", ("xmm5", ("m", "r11", "rdx", 8, 0))),
    ("addsd", ("xmm4", "xmm1")),
    ("mulsd", ("xmm2", "xmm0")),
    ("movdqu", ("xmm7", ("m", 69680, 0, 1, 0), "r9")),
    ("movdqu", ("xmm3", ("m", 69696, 0, 1, 0), "r9")),
    ("shll", ("rcx", 12)),
    ("xorl", ("rcx", "r8")),
    ("andl", ("rcx", -1048576)),
    ("movdq", ("xmm6", "rcx")),
    ("addsd", ("xmm2", "xmm4")),
    ("mov64", ("r9", 4604418534313441775)),
    ("movdq", ("xmm1", "r9")),
    ("pshufd", ("xmm0", "xmm2", 68)),
    ("pshufd", ("xmm4", "xmm2", 68)),
    ("mulsd", ("xmm1", "xmm2")),
    ("pshufd", ("xmm6", "xmm6", 17)),
    ("mulpd", ("xmm0", "xmm0")),
    ("mulpd", ("xmm7", "xmm4")),
    ("paddd", ("xmm5", "xmm6")),
    ("mulsd", ("xmm1", "xmm5")),
    ("pshufd", ("xmm6", "xmm5", 238)),
    ("mulsd", ("xmm0", "xmm0")),
    ("addpd", ("xmm3", "xmm7")),
    ("addsd", ("xmm1", "xmm6")),
    ("mulpd", ("xmm0", "xmm3")),
    ("pshufd", ("xmm3", "xmm0", 238)),
    ("mulsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm3", "xmm5")),
    ("addsd", ("xmm0", "xmm1")),
    ("addsd", ("xmm0", "xmm3")),
    ("addsd", ("xmm0", "xmm5")),
    ("jmp", (931,)),
    ("addl", ("rax", 16)),
    ("movl", ("rdx", 32752)),
    ("andl", ("rdx", "rax")),
    ("cmpl", ("rdx", 32752)),
    ("jcc", ("equal", 341)),
    ("testl", ("rax", 32768)),
    ("jcc", ("notEqual", 485)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("movq", ("xmm3", ("m", "rsp", 0, 1, 8))),
    ("movdl", ("rdx", "xmm3")),
    ("psrlq", ("xmm3", 32)),
    ("movdl", ("rcx", "xmm3")),
    ("orl", ("rdx", "rcx")),
    ("cmpl", ("rdx", 0)),
    ("jcc", ("equal", 609)),
    ("xorpd", ("xmm3", "xmm3")),
    ("movl", ("rax", 18416)),
    ("pinsrw", ("xmm3", "rax", 3)),
    ("mulsd", ("xmm0", "xmm3")),
    ("xorpd", ("xmm2", "xmm2")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm2", "rax", 3)),
    ("movdqu", ("xmm3", "xmm0")),
    ("pextrw", ("rax", "xmm0", 3)),
    ("por", ("xmm0", "xmm2")),
    ("movl", ("rcx", 18416)),
    ("psrlq", ("xmm0", 27)),
    ("movq", ("xmm2", ("m", 65552, 0, 1, 0), "r9")),
    ("psrld", ("xmm0", 2)),
    ("rcpps", ("xmm0", "xmm0")),
    ("psllq", ("xmm3", 12)),
    ("movdqu", ("xmm6", ("m", 65536, 0, 1, 0), "r9")),
    ("psrlq", ("xmm3", 12)),
    ("mulss", ("xmm0", "xmm7")),
    ("movl", ("rdx", -1024)),
    ("movdl", ("xmm5", "rdx")),
    ("por", ("xmm3", "xmm1")),
    ("paddd", ("xmm0", "xmm4")),
    ("psllq", ("xmm5", 32)),
    ("movdl", ("rdx", "xmm0")),
    ("psllq", ("xmm0", 29)),
    ("pand", ("xmm5", "xmm3")),
    ("movl", ("r8", 0)),
    ("pand", ("xmm0", "xmm6")),
    ("subsd", ("xmm3", "xmm5")),
    ("andl", ("rax", 32752)),
    ("subl", ("rax", 18416)),
    ("sarl", ("rax", 4)),
    ("cvtsi2sdl", ("xmm7", "rax")),
    ("mulpd", ("xmm5", "xmm0")),
    ("jmp", (68,)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("movq", ("xmm3", ("m", "rsp", 0, 1, 8))),
    ("movdl", ("rdx", "xmm3")),
    ("psrlq", ("xmm3", 32)),
    ("movdl", ("rcx", "xmm3")),
    ("orl", ("rdx", "rcx")),
    ("cmpl", ("rdx", 0)),
    ("jcc", ("equal", 609)),
    ("xorpd", ("xmm3", "xmm3")),
    ("movl", ("rax", 18416)),
    ("pinsrw", ("xmm3", "rax", 3)),
    ("mulsd", ("xmm0", "xmm3")),
    ("xorpd", ("xmm2", "xmm2")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm2", "rax", 3)),
    ("movdqu", ("xmm3", "xmm0")),
    ("pextrw", ("rax", "xmm0", 3)),
    ("por", ("xmm0", "xmm2")),
    ("movl", ("rcx", 18416)),
    ("psrlq", ("xmm0", 27)),
    ("movq", ("xmm2", ("m", 65552, 0, 1, 0), "r9")),
    ("psrld", ("xmm0", 2)),
    ("rcpps", ("xmm0", "xmm0")),
    ("psllq", ("xmm3", 12)),
    ("movdqu", ("xmm6", ("m", 65536, 0, 1, 0), "r9")),
    ("psrlq", ("xmm3", 12)),
    ("mulss", ("xmm0", "xmm7")),
    ("movl", ("rdx", -1024)),
    ("movdl", ("xmm5", "rdx")),
    ("por", ("xmm3", "xmm1")),
    ("paddd", ("xmm0", "xmm4")),
    ("psllq", ("xmm5", 32)),
    ("movdl", ("rdx", "xmm0")),
    ("psllq", ("xmm0", 29)),
    ("pand", ("xmm5", "xmm3")),
    ("movl", ("r8", -2147483648)),
    ("pand", ("xmm0", "xmm6")),
    ("subsd", ("xmm3", "xmm5")),
    ("andl", ("rax", 32752)),
    ("subl", ("rax", 18416)),
    ("sarl", ("rax", 4)),
    ("cvtsi2sdl", ("xmm7", "rax")),
    ("mulpd", ("xmm5", "xmm0")),
    ("jmp", (68,)),
    ("cmpl", ("rax", 0)),
    ("jcc", ("less", 579)),
    ("cmpl", ("rax", 752)),
    ("jcc", ("aboveEqual", 665)),
    ("addsd", ("xmm0", "xmm7")),
    ("movq", ("xmm2", ("m", 69760, 0, 1, 0), "r9")),
    ("addpd", ("xmm3", "xmm0")),
    ("xorpd", ("xmm6", "xmm6")),
    ("movl", ("rax", 17080)),
    ("pinsrw", ("xmm6", "rax", 3)),
    ("pshufd", ("xmm0", "xmm3", 238)),
    ("addsd", ("xmm0", "xmm3")),
    ("movdqu", ("xmm3", "xmm5")),
    ("addsd", ("xmm5", "xmm0")),
    ("movdqu", ("xmm4", "xmm2")),
    ("subsd", ("xmm3", "xmm5")),
    ("movdqu", ("xmm7", "xmm5")),
    ("pand", ("xmm5", "xmm2")),
    ("movdqu", ("xmm2", "xmm1")),
    ("pand", ("xmm4", "xmm1")),
    ("subsd", ("xmm7", "xmm5")),
    ("addsd", ("xmm0", "xmm3")),
    ("subsd", ("xmm1", "xmm4")),
    ("mulsd", ("xmm4", "xmm5")),
    ("addsd", ("xmm0", "xmm7")),
    ("mulsd", ("xmm2", "xmm0")),
    ("movdqu", ("xmm7", "xmm6")),
    ("mulsd", ("xmm1", "xmm5")),
    ("addsd", ("xmm6", "xmm4")),
    ("movdl", ("rax", "xmm6")),
    ("subsd", ("xmm6", "xmm7")),
    ("lea", ("r11", 65584)),
    ("addsd", ("xmm2", "xmm1")),
    ("movdqu", ("xmm7", ("m", 69680, 0, 1, 0), "r9")),
    ("movdqu", ("xmm3", ("m", 69696, 0, 1, 0), "r9")),
    ("subsd", ("xmm4", "xmm6")),
    ("pextrw", ("rdx", "xmm6", 3)),
    ("movl", ("rcx", "rax")),
    ("andl", ("rax", 255)),
    ("addl", ("rax", "rax")),
    ("movdqu", ("xmm5", ("m", "r11", "rax", 8, 0))),
    ("addsd", ("xmm2", "xmm4")),
    ("sarl", ("rcx", 8)),
    ("movl", ("rax", "rcx")),
    ("sarl", ("rcx", 1)),
    ("subl", ("rax", "rcx")),
    ("shll", ("rcx", 20)),
    ("xorl", ("rcx", "r8")),
    ("movdl", ("xmm6", "rcx")),
    ("movq", ("xmm1", ("m", 69712, 0, 1, 0), "r9")),
    ("andl", ("rdx", 32767)),
    ("cmpl", ("rdx", 16529)),
    ("jcc", ("above", 665)),
    ("pshufd", ("xmm0", "xmm2", 68)),
    ("pshufd", ("xmm4", "xmm2", 68)),
    ("mulpd", ("xmm0", "xmm0")),
    ("mulpd", ("xmm7", "xmm4")),
    ("pshufd", ("xmm6", "xmm6", 17)),
    ("mulsd", ("xmm1", "xmm2")),
    ("mulsd", ("xmm0", "xmm0")),
    ("paddd", ("xmm5", "xmm6")),
    ("addpd", ("xmm3", "xmm7")),
    ("mulsd", ("xmm1", "xmm5")),
    ("pshufd", ("xmm6", "xmm5", 238)),
    ("mulpd", ("xmm0", "xmm3")),
    ("addsd", ("xmm1", "xmm6")),
    ("pshufd", ("xmm3", "xmm0", 238)),
    ("mulsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm3", "xmm5")),
    ("shll", ("rax", 4)),
    ("xorpd", ("xmm4", "xmm4")),
    ("addl", ("rax", 16368)),
    ("pinsrw", ("xmm4", "rax", 3)),
    ("addsd", ("xmm0", "xmm1")),
    ("addsd", ("xmm0", "xmm3")),
    ("movdqu", ("xmm1", "xmm0")),
    ("addsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm0", "xmm4")),
    ("pextrw", ("rax", "xmm0", 3)),
    ("andl", ("rax", 32752)),
    ("jcc", ("equal", 696)),
    ("cmpl", ("rax", 32752)),
    ("jcc", ("equal", 684)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("movdqu", ("xmm2", "xmm0")),
    ("movdl", ("rax", "xmm2")),
    ("psrlq", ("xmm2", 20)),
    ("movdl", ("rdx", "xmm2")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("equal", 366)),
    ("movdl", ("rax", "xmm1")),
    ("psrlq", ("xmm1", 32)),
    ("movdl", ("rdx", "xmm1")),
    ("movl", ("rcx", "rdx")),
    ("addl", ("rdx", "rdx")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("equal", 358)),
    ("addsd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("movl", (("m", "rsp", 0, 1, 0), 29)),
    ("jmp", (929,)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 16))),
    ("addpd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("movdl", ("rax", "xmm1")),
    ("movdqu", ("xmm2", "xmm1")),
    ("psrlq", ("xmm1", 32)),
    ("movdl", ("rdx", "xmm1")),
    ("movl", ("rcx", "rdx")),
    ("addl", ("rdx", "rdx")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("equal", 573)),
    ("pextrw", ("rax", "xmm2", 3)),
    ("andl", ("rax", 32752)),
    ("cmpl", ("rax", 32752)),
    ("jcc", ("notEqual", 383)),
    ("movdl", ("rax", "xmm2")),
    ("psrlq", ("xmm2", 20)),
    ("movdl", ("rdx", "xmm2")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("notEqual", 363)),
    ("pextrw", ("rax", "xmm0", 3)),
    ("testl", ("rax", 32768)),
    ("jcc", ("notEqual", 396)),
    ("testl", ("rcx", -2147483648)),
    ("jcc", ("notEqual", 577)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movdl", ("rax", "xmm1")),
    ("testl", ("rax", 1)),
    ("jcc", ("notEqual", 428)),
    ("testl", ("rax", 2)),
    ("jcc", ("notEqual", 419)),
    ("jmp", (428,)),
    ("shrl", ("rcx", 20)),
    ("andl", ("rcx", 2047)),
    ("cmpl", ("rcx", 1075)),
    ("jcc", ("above", 428)),
    ("jcc", ("equal", 436)),
    ("cmpl", ("rcx", 1074)),
    ("jcc", ("above", 389)),
    ("cmpl", ("rcx", 1023)),
    ("jcc", ("below", 428)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movl", ("rax", 17208)),
    ("xorpd", ("xmm3", "xmm3")),
    ("pinsrw", ("xmm3", "rax", 3)),
    ("movdqu", ("xmm4", "xmm3")),
    ("addsd", ("xmm3", "xmm1")),
    ("subsd", ("xmm4", "xmm3")),
    ("addsd", ("xmm1", "xmm4")),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32752)),
    ("jcc", ("notEqual", 428)),
    ("movdl", ("rax", "xmm3")),
    ("andl", ("rax", 1)),
    ("jcc", ("equal", 428)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32768)),
    ("jcc", ("notEqual", 424)),
    ("jmp", (931,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 32768)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32768)),
    ("jcc", ("notEqual", 577)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 32752)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movdl", ("rax", "xmm1")),
    ("andl", ("rax", 1)),
    ("jcc", ("equal", 428)),
    ("jmp", (419,)),
    ("movdl", ("rax", "xmm1")),
    ("psrlq", ("xmm1", 20)),
    ("movdl", ("rdx", "xmm1")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("equal", 449)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 16))),
    ("addsd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("pextrw", ("rax", "xmm0", 3)),
    ("cmpl", ("rax", 49136)),
    ("jcc", ("notEqual", 462)),
    ("movdl", ("rcx", "xmm0")),
    ("psrlq", ("xmm0", 20)),
    ("movdl", ("rdx", "xmm0")),
    ("orl", ("rcx", "rdx")),
    ("jcc", ("notEqual", 462)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 32760)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("andl", ("rax", 32752)),
    ("subl", ("rax", 16368)),
    ("pextrw", ("rdx", "xmm1", 3)),
    ("xorpd", ("xmm0", "xmm0")),
    ("xorl", ("rax", "rdx")),
    ("andl", ("rax", 32768)),
    ("jcc", ("equal", 471)),
    ("jmp", (931,)),
    ("movl", ("rcx", 32752)),
    ("pinsrw", ("xmm0", "rcx", 3)),
    ("jmp", (931,)),
    ("movdl", ("rax", "xmm1")),
    ("cmpl", ("rdx", 17184)),
    ("jcc", ("above", 482)),
    ("testl", ("rax", 1)),
    ("jcc", ("notEqual", 544)),
    ("testl", ("rax", 2)),
    ("jcc", ("equal", 551)),
    ("jmp", (522,)),
    ("testl", ("rax", 1)),
    ("jcc", ("equal", 551)),
    ("jmp", (522,)),
    ("movq", ("xmm2", ("m", "rsp", 0, 1, 8))),
    ("movdl", ("rax", "xmm2")),
    ("psrlq", ("xmm2", 31)),
    ("movdl", ("rcx", "xmm2")),
    ("orl", ("rax", "rcx")),
    ("jcc", ("equal", 609)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("pextrw", ("rdx", "xmm1", 3)),
    ("movdl", ("rax", "xmm1")),
    ("movdqu", ("xmm2", "xmm1")),
    ("psrlq", ("xmm2", 32)),
    ("movdl", ("rcx", "xmm2")),
    ("addl", ("rcx", "rcx")),
    ("orl", ("rcx", "rax")),
    ("jcc", ("equal", 600)),
    ("andl", ("rdx", 32752)),
    ("cmpl", ("rdx", 32752)),
    ("jcc", ("equal", 441)),
    ("cmpl", ("rdx", 17200)),
    ("jcc", ("above", 551)),
    ("cmpl", ("rdx", 17184)),
    ("jcc", ("aboveEqual", 474)),
    ("cmpl", ("rdx", 16368)),
    ("jcc", ("below", 544)),
    ("movl", ("rax", 17208)),
    ("xorpd", ("xmm2", "xmm2")),
    ("pinsrw", ("xmm2", "rax", 3)),
    ("movdqu", ("xmm4", "xmm2")),
    ("addsd", ("xmm2", "xmm1")),
    ("subsd", ("xmm4", "xmm2")),
    ("addsd", ("xmm1", "xmm4")),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32767)),
    ("jcc", ("notEqual", 544)),
    ("movdl", ("rax", "xmm2")),
    ("andl", ("rax", 1)),
    ("jcc", ("equal", 551)),
    ("xorpd", ("xmm1", "xmm1")),
    ("movl", ("rdx", 30704)),
    ("pinsrw", ("xmm1", "rdx", 3)),
    ("movq", ("xmm2", ("m", 65552, 0, 1, 0), "r9")),
    ("movq", ("xmm4", ("m", "rsp", 0, 1, 8))),
    ("pextrw", ("rax", "xmm4", 3)),
    ("movl", ("rdx", 8192)),
    ("movdl", ("xmm4", "rdx")),
    ("andl", ("rax", 32767)),
    ("subl", ("rax", 16)),
    ("jcc", ("less", 213)),
    ("movl", ("rdx", "rax")),
    ("andl", ("rdx", 32752)),
    ("subl", ("rdx", 16368)),
    ("movl", ("rcx", "rdx")),
    ("sarl", ("rdx", 31)),
    ("addl", ("rcx", "rdx")),
    ("xorl", ("rcx", "rdx")),
    ("addl", ("rcx", 16)),
    ("bsrl", ("rcx", "rcx")),
    ("movl", ("r8", -2147483648)),
    ("jmp", (48,)),
    ("xorpd", ("xmm1", "xmm1")),
    ("movl", ("rax", 32752)),
    ("pinsrw", ("xmm1", "rax", 3)),
    ("xorpd", ("xmm0", "xmm0")),
    ("mulsd", ("xmm0", "xmm1")),
    ("movl", (("m", "rsp", 0, 1, 0), 28)),
    ("jmp", (929,)),
    ("xorpd", ("xmm1", "xmm1")),
    ("movl", ("rdx", 30704)),
    ("pinsrw", ("xmm1", "rdx", 3)),
    ("movq", ("xmm2", ("m", 65552, 0, 1, 0), "r9")),
    ("movq", ("xmm4", ("m", "rsp", 0, 1, 8))),
    ("pextrw", ("rax", "xmm4", 3)),
    ("movl", ("rdx", 8192)),
    ("movdl", ("xmm4", "rdx")),
    ("andl", ("rax", 32767)),
    ("subl", ("rax", 16)),
    ("jcc", ("less", 169)),
    ("movl", ("rdx", "rax")),
    ("andl", ("rdx", 32752)),
    ("subl", ("rdx", 16368)),
    ("movl", ("rcx", "rdx")),
    ("sarl", ("rdx", 31)),
    ("addl", ("rcx", "rdx")),
    ("xorl", ("rcx", "rdx")),
    ("addl", ("rcx", 16)),
    ("bsrl", ("rcx", "rcx")),
    ("movl", ("r8", 0)),
    ("jmp", (48,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("jmp", (931,)),
    ("addl", ("rax", 384)),
    ("cmpl", ("rax", 0)),
    ("jcc", ("less", 600)),
    ("mulsd", ("xmm5", "xmm1")),
    ("addsd", ("xmm0", "xmm7")),
    ("shrl", ("r8", 31)),
    ("addpd", ("xmm3", "xmm0")),
    ("pshufd", ("xmm0", "xmm3", 238)),
    ("addsd", ("xmm3", "xmm0")),
    ("lea", ("r11", 78080)),
    ("movq", ("xmm4", ("m", "r11", "r8", 8, 0))),
    ("mulsd", ("xmm1", "xmm3")),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("shll", ("r8", 15)),
    ("orl", ("rax", "r8")),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("addsd", ("xmm5", "xmm1")),
    ("mulsd", ("xmm5", "xmm4")),
    ("addsd", ("xmm0", "xmm5")),
    ("jmp", (931,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("movl", (("m", "rsp", 0, 1, 0), 26)),
    ("jmp", (929,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movdqu", ("xmm2", "xmm1")),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32752)),
    ("cmpl", ("rax", 32752)),
    ("jcc", ("notEqual", 620)),
    ("movdl", ("rax", "xmm2")),
    ("psrlq", ("xmm2", 20)),
    ("movdl", ("rdx", "xmm2")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("notEqual", 363)),
    ("movdl", ("rax", "xmm1")),
    ("psrlq", ("xmm1", 32)),
    ("movdl", ("rdx", "xmm1")),
    ("movl", ("rcx", "rdx")),
    ("addl", ("rdx", "rdx")),
    ("orl", ("rax", "rdx")),
    ("jcc", ("equal", 604)),
    ("shrl", ("rdx", 21)),
    ("cmpl", ("rdx", 1075)),
    ("jcc", ("above", 655)),
    ("jcc", ("equal", 651)),
    ("cmpl", ("rdx", 1023)),
    ("jcc", ("below", 655)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movl", ("rax", 17208)),
    ("xorpd", ("xmm3", "xmm3")),
    ("pinsrw", ("xmm3", "rax", 3)),
    ("movdqu", ("xmm4", "xmm3")),
    ("addsd", ("xmm3", "xmm1")),
    ("subsd", ("xmm4", "xmm3")),
    ("addsd", ("xmm1", "xmm4")),
    ("pextrw", ("rax", "xmm1", 3)),
    ("andl", ("rax", 32752)),
    ("jcc", ("notEqual", 655)),
    ("movdl", ("rax", "xmm3")),
    ("andl", ("rax", 1)),
    ("jcc", ("equal", 655)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("testl", ("rcx", -2147483648)),
    ("jcc", ("notEqual", 658)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movdl", ("rax", "xmm1")),
    ("testl", ("rax", 1)),
    ("jcc", ("notEqual", 647)),
    ("testl", ("rcx", -2147483648)),
    ("jcc", ("equal", 577)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 16368)),
    ("xorpd", ("xmm1", "xmm1")),
    ("pinsrw", ("xmm1", "rax", 3)),
    ("divsd", ("xmm1", "xmm0")),
    ("movdqu", ("xmm0", "xmm1")),
    ("movl", (("m", "rsp", 0, 1, 0), 27)),
    ("jmp", (929,)),
    ("movq", ("xmm2", ("m", "rsp", 0, 1, 8))),
    ("movq", ("xmm6", ("m", "rsp", 0, 1, 16))),
    ("pextrw", ("rax", "xmm2", 3)),
    ("pextrw", ("rdx", "xmm6", 3)),
    ("movl", ("rcx", 32752)),
    ("andl", ("rcx", "rdx")),
    ("cmpl", ("rcx", 32752)),
    ("jcc", ("equal", 889)),
    ("andl", ("rax", 32752)),
    ("subl", ("rax", 16368)),
    ("xorl", ("rdx", "rax")),
    ("testl", ("rdx", 32768)),
    ("jcc", ("notEqual", 686)),
    ("movl", ("rax", 32736)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("shrl", ("r8", 16)),
    ("orl", ("rax", "r8")),
    ("pinsrw", ("xmm1", "rax", 3)),
    ("mulsd", ("xmm0", "xmm1")),
    ("movl", (("m", "rsp", 0, 1, 0), 24)),
    ("jmp", (929,)),
    ("movl", ("rax", 16)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("mulsd", ("xmm0", "xmm0")),
    ("testl", ("r8", -2147483648)),
    ("jcc", ("equal", 694)),
    ("mov64", ("r9", 9223372036854775808)),
    ("movdq", ("xmm2", "r9")),
    ("xorpd", ("xmm0", "xmm2")),
    ("movl", (("m", "rsp", 0, 1, 0), 25)),
    ("jmp", (929,)),
    ("pextrw", ("rcx", "xmm5", 3)),
    ("pextrw", ("rdx", "xmm4", 3)),
    ("movl", ("rax", -1)),
    ("andl", ("rcx", 32752)),
    ("subl", ("rcx", 16368)),
    ("andl", ("rdx", 32752)),
    ("addl", ("rdx", "rcx")),
    ("movl", ("rcx", -31)),
    ("sarl", ("rdx", 4)),
    ("subl", ("rcx", "rdx")),
    ("jcc", ("lessEqual", 710)),
    ("cmpl", ("rcx", 20)),
    ("jcc", ("above", 718)),
    ("shll", ("rax",)),
    ("movdl", ("xmm0", "rax")),
    ("psllq", ("xmm0", 32)),
    ("pand", ("xmm0", "xmm5")),
    ("subsd", ("xmm5", "xmm0")),
    ("addsd", ("xmm5", "xmm1")),
    ("mulsd", ("xmm0", "xmm4")),
    ("mulsd", ("xmm5", "xmm4")),
    ("addsd", ("xmm0", "xmm5")),
    ("jmp", (694,)),
    ("movw", ("rcx", ("m", "rsp", 0, 1, 22))),
    ("movl", ("rdx", -2147483648)),
    ("movdl", ("xmm1", "rdx")),
    ("xorpd", ("xmm7", "xmm7")),
    ("paddd", ("xmm0", "xmm4")),
    ("movdl", ("rdx", "xmm0")),
    ("psllq", ("xmm0", 29)),
    ("paddq", ("xmm1", "xmm3")),
    ("pand", ("xmm5", "xmm1")),
    ("andl", ("rcx", 32752)),
    ("cmpl", ("rcx", 16560)),
    ("jcc", ("less", 62)),
    ("pand", ("xmm0", "xmm6")),
    ("subsd", ("xmm3", "xmm5")),
    ("addl", ("rax", 16351)),
    ("shrl", ("rax", 4)),
    ("subl", ("rax", 1022)),
    ("cvtsi2sdl", ("xmm7", "rax")),
    ("mulpd", ("xmm5", "xmm0")),
    ("lea", ("r11", 69872)),
    ("movq", ("xmm4", ("m", 69728, 0, 1, 0), "r9")),
    ("mulsd", ("xmm3", "xmm0")),
    ("movq", ("xmm6", ("m", 69728, 0, 1, 0), "r9")),
    ("subsd", ("xmm5", "xmm2")),
    ("movq", ("xmm1", ("m", 69736, 0, 1, 0), "r9")),
    ("pshufd", ("xmm2", "xmm3", 68)),
    ("unpcklpd", ("xmm5", "xmm3")),
    ("addsd", ("xmm3", "xmm5")),
    ("movq", ("xmm0", ("m", 69736, 0, 1, 0), "r9")),
    ("andl", ("rdx", 16760832)),
    ("shrl", ("rdx", 10)),
    ("addpd", ("xmm7", ("m", "r11", "rdx", 1, -3648))),
    ("mulsd", ("xmm4", "xmm5")),
    ("mulsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm6", "xmm2")),
    ("mulsd", ("xmm1", "xmm2")),
    ("movdqu", ("xmm2", "xmm5")),
    ("mulsd", ("xmm4", "xmm5")),
    ("addsd", ("xmm5", "xmm0")),
    ("movdqu", ("xmm0", "xmm7")),
    ("addsd", ("xmm2", "xmm3")),
    ("addsd", ("xmm7", "xmm5")),
    ("mulsd", ("xmm6", "xmm2")),
    ("subsd", ("xmm0", "xmm7")),
    ("movdqu", ("xmm2", "xmm7")),
    ("addsd", ("xmm7", "xmm4")),
    ("addsd", ("xmm0", "xmm5")),
    ("subsd", ("xmm2", "xmm7")),
    ("addsd", ("xmm4", "xmm2")),
    ("pshufd", ("xmm2", "xmm5", 238)),
    ("movdqu", ("xmm5", "xmm7")),
    ("addsd", ("xmm7", "xmm2")),
    ("addsd", ("xmm4", "xmm0")),
    ("movdqu", ("xmm0", ("m", 69776, 0, 1, 0), "r9")),
    ("subsd", ("xmm5", "xmm7")),
    ("addsd", ("xmm6", "xmm4")),
    ("movdqu", ("xmm4", "xmm7")),
    ("addsd", ("xmm5", "xmm2")),
    ("addsd", ("xmm7", "xmm1")),
    ("movdqu", ("xmm2", ("m", 69840, 0, 1, 0), "r9")),
    ("subsd", ("xmm4", "xmm7")),
    ("addsd", ("xmm6", "xmm5")),
    ("addsd", ("xmm4", "xmm1")),
    ("pshufd", ("xmm5", "xmm7", 238)),
    ("movapd", ("xmm1", "xmm7")),
    ("addsd", ("xmm7", "xmm5")),
    ("subsd", ("xmm1", "xmm7")),
    ("addsd", ("xmm1", "xmm5")),
    ("movdqu", ("xmm5", ("m", 69856, 0, 1, 0), "r9")),
    ("pshufd", ("xmm3", "xmm3", 68)),
    ("addsd", ("xmm6", "xmm4")),
    ("addsd", ("xmm6", "xmm1")),
    ("movdqu", ("xmm1", ("m", 69808, 0, 1, 0), "r9")),
    ("mulpd", ("xmm0", "xmm3")),
    ("mulpd", ("xmm2", "xmm3")),
    ("pshufd", ("xmm4", "xmm3", 68)),
    ("mulpd", ("xmm3", "xmm3")),
    ("addpd", ("xmm0", "xmm1")),
    ("addpd", ("xmm5", "xmm2")),
    ("mulsd", ("xmm4", "xmm3")),
    ("movq", ("xmm2", ("m", 69744, 0, 1, 0), "r9")),
    ("mulpd", ("xmm3", "xmm3")),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movw", ("rcx", ("m", "rsp", 0, 1, 22))),
    ("mulpd", ("xmm0", "xmm4")),
    ("pextrw", ("rax", "xmm7", 3)),
    ("mulpd", ("xmm5", "xmm4")),
    ("mulpd", ("xmm0", "xmm3")),
    ("movq", ("xmm4", ("m", 65576, 0, 1, 0), "r9")),
    ("pand", ("xmm2", "xmm7")),
    ("addsd", ("xmm5", "xmm6")),
    ("subsd", ("xmm7", "xmm2")),
    ("addpd", ("xmm5", "xmm0")),
    ("andl", ("rax", 32752)),
    ("subl", ("rax", 16368)),
    ("andl", ("rcx", 32752)),
    ("cmpl", ("rcx", 32752)),
    ("jcc", ("equal", 889)),
    ("addl", ("rcx", "rax")),
    ("cmpl", ("rcx", 16576)),
    ("jcc", ("aboveEqual", 911)),
    ("pshufd", ("xmm0", "xmm5", 238)),
    ("pand", ("xmm4", "xmm1")),
    ("movdqu", ("xmm3", "xmm1")),
    ("addsd", ("xmm5", "xmm0")),
    ("subsd", ("xmm1", "xmm4")),
    ("xorpd", ("xmm6", "xmm6")),
    ("movl", ("rdx", 17080)),
    ("pinsrw", ("xmm6", "rdx", 3)),
    ("addsd", ("xmm7", "xmm5")),
    ("mulsd", ("xmm4", "xmm2")),
    ("mulsd", ("xmm1", "xmm2")),
    ("movdqu", ("xmm5", "xmm6")),
    ("mulsd", ("xmm3", "xmm7")),
    ("addsd", ("xmm6", "xmm4")),
    ("addsd", ("xmm1", "xmm3")),
    ("movdqu", ("xmm7", ("m", 69680, 0, 1, 0), "r9")),
    ("movdl", ("rdx", "xmm6")),
    ("subsd", ("xmm6", "xmm5")),
    ("lea", ("r11", 65584)),
    ("movdqu", ("xmm3", ("m", 69696, 0, 1, 0), "r9")),
    ("movq", ("xmm2", ("m", 69712, 0, 1, 0), "r9")),
    ("subsd", ("xmm4", "xmm6")),
    ("movl", ("rcx", "rdx")),
    ("andl", ("rdx", 255)),
    ("addl", ("rdx", "rdx")),
    ("movdqu", ("xmm5", ("m", "r11", "rdx", 8, 0))),
    ("addsd", ("xmm4", "xmm1")),
    ("pextrw", ("rdx", "xmm6", 3)),
    ("shrl", ("rcx", 8)),
    ("movl", ("rax", "rcx")),
    ("shrl", ("rcx", 1)),
    ("subl", ("rax", "rcx")),
    ("shll", ("rcx", 20)),
    ("movdl", ("xmm6", "rcx")),
    ("pshufd", ("xmm0", "xmm4", 68)),
    ("pshufd", ("xmm1", "xmm4", 68)),
    ("mulpd", ("xmm0", "xmm0")),
    ("mulpd", ("xmm7", "xmm1")),
    ("pshufd", ("xmm6", "xmm6", 17)),
    ("mulsd", ("xmm2", "xmm4")),
    ("andl", ("rdx", 32767)),
    ("cmpl", ("rdx", 16529)),
    ("jcc", ("above", 665)),
    ("mulsd", ("xmm0", "xmm0")),
    ("paddd", ("xmm5", "xmm6")),
    ("addpd", ("xmm3", "xmm7")),
    ("mulsd", ("xmm2", "xmm5")),
    ("pshufd", ("xmm6", "xmm5", 238)),
    ("mulpd", ("xmm0", "xmm3")),
    ("addsd", ("xmm2", "xmm6")),
    ("pshufd", ("xmm3", "xmm0", 238)),
    ("addl", ("rax", 1023)),
    ("shll", ("rax", 20)),
    ("orl", ("rax", "r8")),
    ("movdl", ("xmm4", "rax")),
    ("mulsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm3", "xmm5")),
    ("addsd", ("xmm0", "xmm2")),
    ("psllq", ("xmm4", 32)),
    ("addsd", ("xmm0", "xmm3")),
    ("movdqu", ("xmm1", "xmm0")),
    ("addsd", ("xmm0", "xmm5")),
    ("mulsd", ("xmm0", "xmm4")),
    ("pextrw", ("rax", "xmm0", 3)),
    ("andl", ("rax", 32752)),
    ("jcc", ("equal", 696)),
    ("cmpl", ("rax", 32752)),
    ("jcc", ("equal", 684)),
    ("jmp", (931,)),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 8))),
    ("xorpd", ("xmm2", "xmm2")),
    ("movl", ("rax", 49136)),
    ("pinsrw", ("xmm2", "rax", 3)),
    ("addsd", ("xmm2", "xmm0")),
    ("pextrw", ("rax", "xmm2", 3)),
    ("cmpl", ("rax", 0)),
    ("jcc", ("notEqual", 901)),
    ("xorpd", ("xmm0", "xmm0")),
    ("movl", ("rax", 32760)),
    ("pinsrw", ("xmm0", "rax", 3)),
    ("jmp", (931,)),
    ("movq", ("xmm1", ("m", "rsp", 0, 1, 16))),
    ("movdl", ("rdx", "xmm1")),
    ("movdqu", ("xmm3", "xmm1")),
    ("psrlq", ("xmm3", 20)),
    ("movdl", ("rcx", "xmm3")),
    ("orl", ("rcx", "rdx")),
    ("jcc", ("equal", 917)),
    ("addsd", ("xmm1", "xmm1")),
    ("movdqu", ("xmm0", "xmm1")),
    ("jmp", (931,)),
    ("pextrw", ("rax", "xmm1", 3)),
    ("pextrw", ("rcx", "xmm2", 3)),
    ("xorl", ("rax", "rcx")),
    ("testl", ("rax", 32768)),
    ("jcc", ("equal", 678)),
    ("jmp", (686,)),
    ("pextrw", ("rax", "xmm0", 3)),
    ("andl", ("rax", 32752)),
    ("pextrw", ("rdx", "xmm1", 3)),
    ("xorpd", ("xmm0", "xmm0")),
    ("subl", ("rax", 16368)),
    ("xorl", ("rax", "rdx")),
    ("testl", ("rax", 32768)),
    ("jcc", ("equal", 926)),
    ("jmp", (931,)),
    ("movl", ("rdx", 32752)),
    ("pinsrw", ("xmm0", "rdx", 3)),
    ("jmp", (931,)),
    ("movq", (("m", "rsp", 0, 1, 24), "xmm0")),
    ("movq", ("xmm0", ("m", "rsp", 0, 1, 24))),
    ("addq", ("rsp", 40)),
    ("ret", (0,)),
)

_POW_DATA_B85 = (
    "c-rlo_g{}+`1oJ45{goaBq<_olDc)hsEi~nnGLB(gCY&#CG9<>DG?<j(ZJn6$q4Pe_uhMcbME)&`}lr-`Thmx`Ad(}Irll&b)D;6"
    "=Q>x=Xc!CzgTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2"
    "U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L"
    "3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|$1Fc=I5gTY`h7z_r3!C){L3<iV2U@#aA27|%;$He^n|N6;44hNDq"
    "ay2IEX8reT^!xe$e$r?IK>fTXpGBUX+OTo}tR5LWPabn7_ef7C?B^PQwBPCBJ1#^J_n73@UEVSPscN}wl37mV1%|Cc_^tuaWj?2M"
    "-`|SN|Fl-DWbXiMXnfVT_OdbIa@VqhQ*i(+f7tTyKJh2tYL8j#s||p6L5!UJS7+je3ukfCnE^0<Z}YV2x)0&8nP6ox9)QrVVW)2W"
    "3L)#pYIm4j8-VS^+ot*eZ&D`STBPLGg1m0Z+Pk;jC%#A6a4WkFz`S$vu}s$sM8k5Ev5de0C<GS9MaBd2{_wY-3ef`~b3u~Z?nnT^"
    "vu|@mUcvy#Zrbl=Ug$!wc}$w0P8ooe7iv_*o;@U7%v+QPvj?D`w`iHiWH2#)*jgkof59Fnnz(BC{D~gjeOu)#2H=V$v>g8&LB<vq"
    "OZ7Alfaa~-?d#>}L~cU8eq8?mY-G|VKSTwS8;j@Om`o4AtqirC-Uu^NVQaat#PUHXoekvbKIB7aoMSIo#4!kR5lZ{k<USx%cj_fp"
    "^9_Ra^x|>tr;%j7q<MD6&OykFGk>=(MT1OSGPEvUW)KEyj(qf6bBSyaO?VxCa1f$p2E((&gGe#S6G0(rgOI3{wXY+<i`4Lq`~L9k"
    "Ah0C%eYiq*BEEdJ(tc_(2vQrmoaBd26Sp*O6Y182aMQE=!vX($WcH^J*OEJfV089n6GUGlx_rE4Cp`zjoGr9)>zV*kTzBv3ZJ~p}"
    "d}q+5_C+vZ^XqE&xhI3ra{1^j)pNcCuP4Vu*qcFM1g1W9$qFS(&M$Fp_%sO1$HexyYK4(zyuu;k-v{Bx#2SX}3V-6ohs%;~C4)d1"
    "#nLPnMHAcU@AcXn2B9w1o4I240lBGiMnJuH5WLfFF+HpgAdml%b^bg#2<P8~#t4o^kY(P6?()lqAjDbao=u()!4q${CzE{$e!Q63"
    "C3+@^cu;dY;OOQd=!**uzLVfY6tdgL)`|?lqcYo*)4P2LSwkC32iYOGzBDiOPEr`bvd(FGv+@u;NZ<{~|LaM>v*Z(hG=|{m$VleN"
    "&z^+MA3iG=y&>4O@vBN~V-Qj6*kr71HUyQO^f2iRCt^qarroS|Ltx%Mxzur4G;#0ZXk)$e5ZqY}-g2tp<h4%$HXj3qAcL1KY@P2!"
    "Hr8z(jfx(ElkBhFbg;V;9BhRqo{2;7+@Fg_@l+V;Us+XfH+^CK4YFl5EC)#Ojkf#l<PL$LM)x!2MIq$M#VyZViiV){K(+Q^CV#?%"
    "(`fU9`XPAONKXIdiXwEx6%yX`48i@arOIqStq3#s43(nEAqc7x(K<;OlbmUiEOX0-p~XqE=*oyIF`L}iE46MI3TK9gpPca^Br8;B"
    "u5B3x$0gjp?U9~@R9C!wy4Wyq55Ffmlq1P`E~8{-Vi=yCk#XL#J%|vUYBn)EIt)+mF$dY4y-yB43e?Zl83y4)YUlgTdy(?)b+M90"
    "!=RUL9-}1bP5w%d+xy&V7@E2cW_8IuAXRMmwr;yS3`Fvu=%1ruq)Ek6i`U-6kg+6;@Ck_~`{`C2>EXk$dx!5#TtXN*{-||#_48q9"
    "9=%W|(_%x8nD=DeO<9m{{%VtnY6#I9&+%3C>o9!Xp}TitKAODV*sIi9Fbr0z!rlcPcL{;r?5fY|hJlP8Si7QXVShDv>#y|;!_Nrs"
    "TNlSXNnXawCCXF7Fg&R<xwRma6pXp_Re*T}juecfPSko4JH^JguyBolU7!T7>98K@d1%G<>8&GByY5}K=%I&XXuNvmsN@KQ+3Ppg"
    "=G`MpJ~+b^jKJdTC83!NcS6+Tf&sJI2ox~-mpDWmA*70)ALKtj0=}E4op_8clc#8#dJkL~Sva3Yg~x&;iM>)@CKh%hAbm=ycYr^V"
    "EFeCo#JY~afT4ftlh4<QqSt|qjlm-j6Ma<ABl$jAS6n`@^T`P4WEKt^{t6??(=57fzg-v~DttFx=pMO!r%Y*8)(A8m?0FNac$--F"
    "d42kUKO>-<!D6~Y&!1RbI~$f<v#_4s6|%bLAu*p=aZj{+1T-CV#cm6Qkk5BT-AtYwf#y?ZidMV}Ci^6n?;c<t1^q*5M<WCsh=V47"
    "W2?AEp+6|Y)a9lh*{=p2w}nQ*s=r^+C(My_IuWHKvU?O>5pOqTIxxuXuf|524vxYdeNi5ZKsSOdQ1|CkjZuhb?d^}e>_Zl<>8!nG"
    "FbV_RzFd~m{$$nm6q&<U7rqbLv}o6-Fye1cQ}y;cqmc9Al&ALxe{wc2w1nMf6goDApKA<pBJ!8dZ)c7i1-7<JEq|Iq$sO89YL_Q2"
    "e1G`RQdOx3#A1i|>9rq6VS~a})yK9GWZI!Kp4)zmLaeLly^Y5RBFHPuU%6rw6m{OmKQD_Uk8F9xd9{5M^x7B_lg}autL_^9Cu5@!"
    "`1f~nZI=hRqUPp@#-(F$xK1bHU{eq|GWNS|C+8S!S4~$@I2KK~oRmwtBRB@3@9B3w-wz^Zckpbgl^%muqYs&D4nHLLzvk~gq&NoB"
    "9#J;L5pOchkDU9UIR+~fp8qIq4kv{KPCCgNj=^r;Gj1zVBgipn=Dg2V3+)T$r={F{$?FNKB`5EVfw984(rZ}*LN+A&?TG&v=qh!G"
    "XDo3ie#_rAiH;cq9iwE9-L(;<!g`x2&7?74jSAm2D(gUGRjssP&mM!-E9WoicvzFlH%n@3{w}P4eK0k_A(9Z^U`!;}k3ph4aak_Y"
    "jBJ%V^DwY~43fWZh`zC4f9GJ0$=mZ|FvjXC#74N2Zek-QH`vBO|Jm6RrLr@`4gH=Do6X}8=HTvn*zz9fS<vO`Bt8z-yUKROumqAf"
    "?!_GmhjAcEjm<0L7xwd4`JRju<G^d_d13ajKk?(zL7i^>aVWNsJatCUpIl*?_*U@RI7}Q4;Ig%gAV9b7gehYjM7fw)(oG%`W4teA"
    "KlqP>LhTE~_@hCD+oJC4>mHATc-WFYTTW-P`tQvZx89C}d(CC%l<o*p>a)b6-p}JucATqFmHiPh;5u)3rDz=9r&~`~X9N(2YJX*h"
    "o5taeJ?BRz-D^ZZPJpx9@Ho6)8}xVWT?Wa%K|y=_k_iwAwJ>yb3?wU;6}~E3Hvz{tajxEL6ijgZQ4RADnt%!^&XP^4QRMi64}7XJ"
    "6HqErFBu*YM!d?~dT7Jp37GzU;E8jYJGtfDqxB=FCZK>TdE&_Pb7XIzQbgtD3HUfx5;5`Z5h?Rjvht_>1Y{hpE-Ei_A;L^NEAu=j"
    "KrY2`_)BmY!FJm2X+gvU?Busm3ek!ps$+H@Y<)Qa+mE^G40b*s?ADikT$(unmP(2<dcUFxZ>1D2slOBOqPbH_uk;#OX~L{`rC|cv"
    "l7C!PSsO~q*m8!w9-IL4(B@c<d>6uVmvF%x(<BtZoXgL^5aQc>z{+#$CP7f>w3vNa6xk&HLhGy0B;2ju_e@{;KG~Z4J8AFUNg(f}"
    "+{@FyM7BQE7fC-d31OnQ?aRLUkZhXYe<_`vgna{X4;+u(B;Q@T8D48P2@k&W+<g#tj#O8xd*pO`5(-^5I-cW>B4Y&{TBQ9Zp~p@&"
    "wkpw)__+M%wZWK4kZSuAka0bLTs^0C{8REIaF>o9SF4C3{Rf^n1>{UZ=8#p=AxB4|H2oOQjj~CQcB*}n$rVCw-P+7^v11Y}Rom=-"
    "3fd9TL(6^irY7Of)ZmLh3C^T(tL`n6RZ}2c%By?yOc41g-M80)Zwgr3z52LKA_-|xm7WNRDM*y5xqV*Z0a3wni1Fj#6!5=&bei!z"
    "oYWOkNM3w$3K|diR9lKik(vf0o+_87z+~|y2^}_L;`BQSj%fQS$h(;P^Ukjb;*8j5tvRnLNZ|aKd}$(>%$l`7X%;;NlC$HiKc@VN"
    "kCuD3v?fh~vT|pYWTZRcFkGBv_H_yh%-etN4)h~$Y$xRAOQ)bU{cWmze<<;)_-xptjw!g8ue<yA<4|ILNT5x1dJ2B)NwUo(2a_hL"
    "K0B7PPJ>VjLv^$+g4FZ~H~+&w4f#6DRhVjniD}Lg>9Nw&z+CPup~o;J-yTilbUri<{*LvX`)}SQ<<7MFSf81OW{Z!X>a8Nlow<WM"
    "EX}9E65KV1;{%DqdecKU?@ojKOYJ)+PTP<zN4F1o2TsE`<6qib))A!2vd0ohanm5SLz}gDCYs!QH9V~$eHxY;n*J!%1hVM!F@L`N"
    "X>g7fbtu^HL@bXT{%Tr34O-{A47P3~$Q69$=e`V0!}Ulr_&FO*?tgdSg7C5#*!^?*@mWtFGE&o}HiBmcYLBRU7_YfU>@uFJ<Q1KP"
    "^0@Eoxmq8P4h8f2iS!v@`F6iyuW|$-Fg;~=SbGNEqyz~r7Y`tg6`m3syfm|Le;t`W?jA@;|8Vz+zcmAAP6}myy6H=%v@Z*`@S6dp"
    "^Nb_pODm!}N8=Rz$qbA#uP)3SawARs`)l~qW}y0LXW_5KHiQkAg&5nf83^>Jxv~k|Ca1pYo?KZ!1J+SaTJjY><c-90=QxLF;MBZD"
    "dM9%@>FBXsMRfTrL^{|j?j<A1%RiV!v^LH{pG^1`8J!Sf$YV9LoA@l)xkOprIub>eJ^tDCU2zuHah=W5s$PhHPp50RPtU^gz30lA"
    "dYy>kHp7ma=CcrEd{4!pL!Wqf{|8qyV-`B<d%ZsM1&}rd^H#bcvyeF!{z-IcIN>5yy|^u57Nk-vOleyq3C{a+WsaG%(BfqlICwLH"
    "G<d&gcuVmteB~anJ5?1(oL<IjRN6iZejn|9HRB>l{fJxAp)<2^{uuX(-*Ext`rABam)6dK(%thJJ5sF49gj!X9ojYr57s%{+nyRq"
    "viEVxOUuuJ*SA^8rz2tH7<jddsn3C5egeZI`aW^f;*#J#<2l%qCSWrGuH=2yylD-GIcV}(^;4iUkf5jiwzc=0gSXmAj9}&fvdaHy"
    "?3<@^5F{MAersejY5CL9b>zbw47CIah~Ez;1~2)F9{D>5-mlia9}bEn*SK)UzG#^PA04-+KHma}?Po9aZJe5eq|~RbBY9E8&I75u"
    "k!<szyouYGCJ;o1el*)FA~X+*zN@q19tROOtZR?_kei3Py%h>)&)So8Wy^Cn)#t(MafN7OaTqb7<ZdrzG7k#7_wBj$<PothGxF8!"
    "t$ASCv#fyqQxxez2r^X!%!9|6{quOS3uJ|V^u5o|=YcOMZdmJx8?ml5Q08OCJf!-r;Jkjxo*cCD6Zuj+5AF8G4{mfD5|vwbnpJkr"
    "L-Xvx8;hUaAS5q&w%@Hd3E44A%9+hxg00%etBJ|?!7tZoJ|pW7^zWORJ1Eu$|Es>Rp$yd#{;MZU{NFkPRd4v8Hu}ka;fIBt@%=38"
    "b%K417Dr^AeHiknS~w+Z=O*WOsXS#_%{FctLreVO)6x4cBg~&e{vXRDdKYv4Z@uDw#^1I}nc&kJQuy^>fBs4Sg&}1b|GR!cRXbP)"
    "`XOYq;R7A+a|#RX2A+m~h`t)oYNsic`EP)DK|dI-33o};Kl86Y`)GDQ_zfy2%SLMc>u)ek>WAkH;a3vu>i^mXelh*PFWCOQ@D>`+"
    "_~_pcH04!aZOnDi_%232D8e@;ZVoXtAHP*U<mZ>X+nK9`);oWpA3`}QtIcn#{cFcWYV^b9-?_%$MbUaOO$YkHT%zz0tMgejpQuzn"
    "1hYOYdSj*jZ@!p20{u|;QO>qC;4~Uv!rl*NBW5+3`RCDi@x}cxb=aD`pD6OL&F~-YgF}2TNcm4%NdB?rJ`lZZuFvyL8}(l(>4VG7"
    "2Q*wQj-l@hbNb+>-=&_ha2eEpIHeCxZk9N}t|*GW{}R^+8P6;(75E%S?Sl{cASWRHRKTPLk}uD-5BQFDw@gNy`q$>ywC#gkDmAlh"
    "I@15fXE$EzgTZs>$|XaPJs3An_kpkc!Hkv@qx=8Ox8`Uce9&N(juh5L_I<Oj5A+i>T+3dZMEYv&>;vY!hk6M);z-_^4SnDv<*~v$"
    "Wb422^u(15^6fP0tI$1&#_P@Wf=p5HSHp{%NS^h*z2N&|N#o%rRkS}PwY|_1adw+S+PQz@>7jpmK|J>->sv<^<S%+zy^#J+m0j?f"
    "5RykEsTVTmO4|CQ`TvdQpN;7S)|mW#WYvD8UvWS$>^$k&?=Ow)OMm0k3rjRR($!^=eH#3(_X6|Wnf=0P$Y1C-M!itj^<3^4<1~^-"
    "|70&DoO?2n^bq+2?Zly8;H-5Iul7ER^i$m13;vIjlJ>Y#{znM+LWtDbCZ4ru{~2;Ty&$|k>rJHCQM5n%S$bhO|7i>B2Ogxq@^lZR"
    "XA&RP&FE-7jh-H;z0J0E+2z$}{)@Fez+75>ThRmgAH)7n4_FNuL|nOq{GSn=)dL1);VVz9N9!BBPwIil{Z2INEOfs3D<AiON6$0a"
    "Nm=9{45pwS@V&iKZnjzrtta8!1G~+fzWvDEj_h^OrU&j_ytYb9<_wZI!lVcC)P`@TY&eAMReq`mI@(+5ulFPUXgo)IfX$XkCu$4w"
    "hipB$9_U_c-y@`p>|>B1(gQ-V(eGAfBY$U1@b-Y%7KaD*K2*OdYY${RTz)!HOaEV+7B}AwW1_<8H_{KG{bU;Kh8>sWn&AQRKblcf"
    "H+Xhv$v4)>A^Cn5cZ0L~=`WA!&LjKp$?b-|+&xbsXZNA+<5Iifc#_a{&W{JtdOY#nz@}})x#y7_vTtBmHw2E(-~VHb{3C|Vs~d_h"
    "R()XEfX*Kyz_A;i@?Et!b@L=zpWCt<vK}+^Qmc=n_7nYXNO>8}Yb%WGA0wsF4ev7P7TzuzXufX;yW!S1dU=rpTA!}JdqKYZh9^1V"
    "$bR%0p>9wYvGM)#g!0#@_1#d{9vFY`{bsa3iYvOI)2esNGEH>;`TM52;0c3+_0~D0FMm`|7qA-bCkj3x|20sr>jKW_p?<l(NI!n&"
    "f-cx6oVeAqQyi_I^SKMyN<WQ^RUmsdIKS(H<Bm4#RBex-^^eANK^N;S$4?rR|8RtM0mrqgqclTVG`_*T3o?BVW{#>L{Th-Ty5NBl"
    "tB-NO31nXn^DZdOeOWEP4C%*jq}K)4DtW+r74lzxMfEN)Q|MYzV~pY_W81+lFc+-18(XS}<YV341u-S3=pq{xQF}_L3sP>mI%VEG"
    "hV0w5z6)4JWP<m-qUNh#(FO0cG>@&6MgB>vnC=7<!Cb$HtFoxSw6_zKhKmIb->2ejS$!u6?D@Jui_}HqYYIDI(|ktPsu^_t8d|@0"
    "!gbc-Hy8C#JZ~6I>4Yl+;&GE5ifF!N@txpfn%*OG4(ZR}4ex}gj`u?%sYj5#_Ih{1w0pRt>H#G*zs{XbIB;rF)khBMKC-*k3CsRe"
    "=^y@p;twsxuoHq~%tKt<P@DcsdqEymu0^NLA^EbW4t2t%z4C4C&L@z+i0$iygfEV*PkMJFd5uLD^h>evjxj;;J^S&dPH-zI-1~N?"
    "9+Iz-trPfbv=W9Nqw~cOV(J9b;o|D*vct%p79$<t(HX(ZB7(-pd}!-{E9F51w=43mh82|^5I*CyCHlnyq`%&;4v5lv*T%D&vS(^W"
    "2YmHzJ$mDvJo=tJsRR7F|2}8W(LwrMkL>^+Qqw1W$2#O6<-r|bzU%98RRhZ3z^wyxd|g+ys_CG3^3uKoggajAREQ&gFyJ-sfS&X&"
    "M`P)uNI!qQ4ydUru@kzB>_J<h(E$vn->YKVC6WDH6gz-Z?c;7+h7{6wsZ0l)4ZZfPwGYV~<00Gu$+jEESYpwB#;o1g0rEy|9Ig6j"
    "z3iyf9ncY+?=(56kNQPv9iSVz%CkKQ-CqWuhuUG$)yD!c(P)48&$PCKMv3>=i>An*vq#F?!HQ%GD_^XP<O%-S4%ttJ>UtmUNA}*E"
    "(GE$8M|<Z#3nKg0y=jMQnMuu;a_C4O&)9Y#cpkkmpQrpqHl!U=$5hh_e1(ua-EQrWw>@A}l0MphdaOe`Z2BU+CW8mX%b4>P?a-2v"
    "<QO|h`SS*Yc6gPuQRGtx%C8z~G}}RKY~STuqX&?@vC8dmXES>aOAfl<49sQQ!CKU%%uEfP-|T%N?J(|N7T`B=3VqMQ*A8d4I2e`+"
    "p?o2`eoZ?_)8o|dh*0r0eQ`Sk=&zJNC5!CS5IoifvBG7}{sZW|&}=%}AlThP;{I{uPYtJQ+Tev?mc&nWBtL`xw+&2v3`>?LA^o#O"
    "zO=!u))%q%MUtq!A*BuO)U&#(sG|Ibu{ypD4g{SXes~A%SHt3nHi-6ciC@c4<zKTtZLrs(M#M=)0NH<<(FPw1cYfCSOWAw&dK;V>"
    "`@K<Ad=%xYOqbe#dC8z|!$su3*(_(<;PTStPsQI-<JTW=gTt!1R$hA4eYKt52KVnA%P8wY`p3vgw?UEDnF}RHRFS+I+uGoQkJi;i"
    "&M4l-nDev&|AF1>#=@z5!fRC<xaB&XIl-rZ+OOtYp{qn=&cOqH&nOydg~skfvox`jl>Du&5T;}L)T)F!AHtQb@S3}jals7vTg>VF"
    "R#+*mDzT%6%GbQJTA{vfh$SNd-IontlUw0*;0)*9@WV*HxwwV(@&W_ZUAd7z?+<GQM)7;;APdUB?|QdF9@i|>1?v8Y$+_DKsl7{8"
    "-k(JIM9k{zt?)@sX}`89iXXJICJXcZRbkrLhRy@+#hF%EQ5&7VSR47D!K`X4sGBxzW>rV?8)(y8!Km@9`Fnd6B+qN<R&ZlF#%aZg"
    ">>aaedn+s&xxUP-6~%`Jiw&(1d2yqSsV2%VV~SR{La)dzN4M{F|MJyrxkat8UM=yBjSXd=XCp0e*;PWU>@}62adx!8&7BIv&V$tb"
    "<yPGS3JQ<zFRG^E=j@*r`1HItflUwPM>N|nEf8now^O49#l!63lorqt<XOt?g5C?+*ArS`)9>dhDt74pp^rzlfF9FU-=U-EywL9W"
    "w*V(oG50<;8R|ZEZh_&Unu~KZD&B<Hw!jKe?n9N=seECZSqr={Wc9l@gyLhvN4*wUm1A?N<OR~-KvS~?O!b@CtTNDjL+@2?f!yea"
    "ouR8K{k-<IK=XX%J2DEzcYaaP77#n`E6eEBquvwzEx_$)e^vDu@+W?WbuIATYl$TLT9j`ygqT}k^69i#UN<#=$#gUDtmRi<l!oF7"
    "-L=0NcD*~!(y@v1NBQPv@LCtSYV0%0NBKv}n&EIT`;Qo)?3eVj8DdgeU-+g9p#H0w&ETmg!Nfd+@+||&<YqYS<bQW*4YEINJgyn+"
    "-mKW*wU`;jkF2m}_^i0>=)p`X9(wsSgJ8L*p0x;p<~w(<8B!luef!I?9?2tW(+oRWoGz$-M(2sX*t8j5zqL%v-9_c=HRqebC|h^V"
    "?lhHurK>kX%ZFzxBQBu(ml3Me3@<L&x@gT)=i5QH8NAD^Cyt*$_K4Bn)eK)k?=XuwqxTEr2!AtV7nEJESD^Co-Rqj+vCg_xudJ#2"
    "V=Hqrls<iYKi`<LKj%yn_+LNkB5Q=k(^n2Oft!;@Y^(sf9~u_7G{My|9k1CqD&L<kZ-Vf()tdXoP(Eic_p1pO9!X86Mkqg_)3Tdj"
    "P1Yi_D3Lu#zoqY+pq|$usp>qH53i1Ig3A*rdG9VG|H<Z#Yy!i2J#Lfz)P1|%zX|dicZ|m*Q2rz9+yvY6q>ViC(fvp}Zr22o+w2ak"
    "vXMag7@0Rg+S;Q5tUIXn?;12g<MsUgzfIBoNQ=^Lf@@hC+aH=D`Li>QG{N+TBL`{K)cd26Xaezx^TSpfQG7LEmTUsi4M%)G_#yin"
    "NC`DTjpc{4xo?pD==wZOuy$WCgJ)tnYWuBj0&~%;vR)sl_uQ97P4Lp_!4PLUvM>L{Xe0Pb4;ZbILg$NLva1mujNQEvH$df=7IlrF"
    "(H*I<-3QIj|FWnN^impBw!A?5&ENNJp&hOxe8LmigJ1enBP>^Vr_I8F&Nu(9H;rJo<^)qv7Sf0I?MWj{$=f9z2}Jj41INQgkV$6}"
    "Ph(O;=iA7;5lVj437=TD0@*j6(Fn^%ekmW?jPh$bn@uCAKB!!5&w|=CQ`1HeaX;tf%GiqRovYgj6J;N-Kb;x;cR%q9X*NRSO&6`3"
    "K1iP!w?mC!R&$e!c@y=%@0DwWySzE^LY~z7?WA}k47_N}vDHNRbWHZvMrf3kp*z0Vg7!y@dttp54kyjl7W|t(`_ZaKFnMHq`{M=l"
    "-p=M&)CkJoR)|=hM(2-zNmm0LdbO*|F#(+?ep+z@XtVNceLhIlLza^b@GQ=rBkBT*X9gSM8bD?Ll|Y^W<c~43z723%@k>0PAo5p!"
    "L)!*$xFabzwTsG!Lk$|>#!%$!a3*?B(#nrEK-7B=8H*zH{-Fy<H$cvq*f{fV>b+*i+W?}X*S2QSkiN94r469^`3$VAK=z>f)YXH<"
    "%}cLJrcgYlJHD-lc9j!G@-2L*|DJO_6z!Jscin*Gr$?TuhZU`zZxkH2q4|FAtcR6V^=T37P&}q{%+-OOM6mpGH7cLJT381cszP)h"
    "ex~GYd|C%T3{2@f;gu+#xNKJk`}T+z*{wqHn6X5)4))~s-Irpg;#2D8I`}m|z2E9KdT-Ki57$CN%f>r?epLPAOkV9mid=Q*^pZX3"
    "{HR3K!qI%oUS%5cUxxbCS|Hq`#i}@Wp!v-dYeDK4Iq>5$+CN6b`dYBh%Zj)Xi|j>f=&pf8=`P2#Z`Av0Uv>>Fo29pZ*@ogd{dsT="
    "Z0LR!?PG!7&)GXnYvAl;{6I1bRnN%YUjy={O_pte$e**#*lXZk%D1zryM>XwBJI^MzwL|nvj=E@Y4e||;nR(slN_fB)Nc2$hHRq;"
    "hn31u{G&A+SHro`CF*`cl>LU~sv%f1xn;RCiZ9t*YpQ|exNh4vM=IW`wN^n{?TLG_hUk3K!#`F5$BL*%HE|Tr7?XZgu&m&(V)rb{"
    "pXlbsRiMUl^>X}S>b@P4tAaHpH0!XnRNH$^6<BU7N-S)l;)7gUCG7IMx^Fs*df!ifs)Sl0k!Ec<<iGU40hO?a&Zj73uZ-49y;KRs"
    "`+IL~`iAaD+S~n=U>u}W&SNBj<jv%$gn;%#>t|+Ayrb85R)7~%!tjR!NdIj1><Um{<*dWfw2j*D2Nl31d6UOvgnC~ln^%BiozykY"
    "9aQ|}Q>=i*NAK#oFQE8LkK(C-hF^<x-w9FmL$QH!NC@vF;;*9j7Nh7}IeajTEi~Og#bfuVa*+A5%#~RV<*N*h8|9GJSm<~03Odi("
    "yN;E^73F}IpP#9E#Rh?LD1R2F6#fk5FSHGlWe{AySCh$)4ei&if-<n&btHA1MDx?spO?XfSstFIS5*GvdZ!GIhdI2+06^_OC(A%}"
    "QS~MDTxm3)uxJ^i=?KRcu2_fU3tCbJt0k`Rg;gMbWUQ?zh4UE#?Ack!|FdJ>l|u0sA4~h=)cgIQS1Gi;Y-w0b<xh+e!%~QESoV&s"
    "p4#7Zxl+(3Zy2BHKy8LEdnqgz@b7ZJfX;8WO;-unZwh#{XFYZQTYf2l(Cc}Vid@wBvkNczpL`kh2U(Xu<?)zO9ZPiIWoN0B!017G"
    "!?$s2e`f_s;QNr*rZw)Ae5%vM&{rGpuDy<Wza$nH!(lyn1?!Dey^;52F`Us&{34PhNxeUviy``0bBXvbsvaPrTMW}ntk;)&Q}yHG"
    "J;mVUT|CpMgZ7`{###*dDx*e%hA1DUskRqErH%cIxoosPV@q}sK%#}llX)uNSRPgc9M`8sVsB9In^~(O2%9;&bcZgg?_@7IRs`22"
    "Qcqf}qRuC;U=hfL1b}TA)vq{P2v(r|IMHo4(&tuLAvn5zSF4E~`<H*ya^4ier)FWr>`HVWGI%`-!MTc8%&k_QdY>B>!fQ#bW4`R@"
    "Jx-gGF9f5{uRlC|iQYrmuAGIy#lcr8v5bm$oBIo3*XNgxJeq*M|NgxI(rlZ^YzdSv(eA|-z-^_AJ8d~A|3B(j04eu#rh2TA|7CB{"
    "DS&Hn=`tB5s9uo0LZSf1m$rU%Ure3fMJxsI>h&Il842q9wcr23OPd?lEEz~&1~~qOnf2U1y7JL`gyAjm7dlIqzE0;kO4T!4{y^Ig"
    "^Vh*EDShsT{Q+NvIlenLsC-sb?GI#C+Ep<>qwc3sravIIE7SAU9u=zol=d4|D~GJhw`QjDBlF)7v$D@M<_uNeSSs)v+~avWzA{nu"
    "&%@>U@Ig>X{_8BYzt6q%!8~PY@iS3=)W7XuKCCef-^aTX-B*k+<G(=G{_YLy>nNTw9AEu{m_uK#?ysQUXD2WIg4T%WzKlIod{^Q5"
    "1!Ojt^9c)TJ-xp_!Ea#v=*=psp5y286Pi|k)m^oZ%8%>he?sd0r6HyVsCv`Up&y{dc~Sc9YZR|(#qmGjS%_QRk~m6#d;K54H)6JY"
    "PJlXZ1lJE}|GsXAQ317|n|^<XCp{8!FW#g4gt5W-JE)r^Br9p3qVj9`@9-=8=GMF$J5k$gC=aw!V=7YbQT2taggkJv6Owvwr$YTb"
    "=|Ub<diC)|&22>EKXK<l4q>qB$1I9x45NZ?@Hbs}ub4I;>fho14KC5c^Vnojyr-?Ce*@E((PPdmR6Jsy$c3kj=V^k0l>G&ga)EC;"
    ">Xo=4b$^|{oC}%U5ynqusrqpOe=bPM^qH8JQ}T0F<^YfIH@@-hsQ$xv6p#a^T3_lUwW)ktNhJr4&Ag27FhuVg+LFaNkf^Zf@1xl1"
    "fB6KX{?k|JdXi}WJq_i9jItYFp~|%|{jUTS|2jm!g680js8knJ@1SwDe}M$Y*XsQHsP~Cp%oh-=d~GhckMh?qXTE^i;*>~9R_c2?"
    "#}}|G&S6(vNu7tv{Liq=?LfYRJGyUazOD=H1DgXc`J(g6I8Xl!d`hPKG#FI8J2aII=lTy++WS-ak;?mQNWQ0VHsB`p-Y~VyhW0lm"
    "QPYZ4{v0cu4Tg^cS%QbDdPrAp7PN*w<lh@j`A@D~7Tn4>?JOyb{vJaseUl04?<>+(%#eT6xP>wyHSI}5(Hkm%_7BehR;wWq5qWfe"
    "X~dcgNW0Q~-KU&df1@i2qi_C5ovoq%-Y7Qn3DQ&>GM`#e{&K_m6WE5l-Xp$_`o6E@BfPJA^=rVN%AdmZKf=1Te?qJrDSJ4SeE>T)"
    "M+;FBz0YVq$3KA6^8>=9IkjF<PC9(sQDQkcPwl4)kq)08J#8`CLHWzbyENdd2-;#jMZKR2MAAUu^R-%U2TK3?C#j(Axn^+?6|ZQU"
    "c^BID^Ahya)OidHPJva2YU@%2DEVYor-1S!wvaInYJXR{zK6FpyH4-3pw2t{{5yD7%w^5<oQgjxcJE+z>(f(@BGCO$dq0>A2fR2O"
    "xZhLpU(GBTy2`V}72;66g~rqR7Jd-{+@JNSdON57TiBu&dq+`t32GmxOaj|T3rD^&%0AIrNuV^Vwl?jjDpe1Ud;_P(Y}Xr$Q-4n>"
    "3V01y(${}&xIpC(FWp|jw3<np+8C-2(%NpngoMTWbz_#JdH{`aBN4h~i5rdE_M(0}vllR^6}wEPjFP{=Fab7d>pyYerrPdj<Ka+?"
    ">oN6vls=J~&*AS+4<XMW%D!ukJ%gdOW^aCLqx+23q!<VNSJgvv>rj48TeJTuRNmHaFZPk8zL$9dQV%$u+G=#6{N7a}7Wl4;?kPJ<"
    "?RWmp$B-7SWSdt?t!F6|19nw*Hv|t;`C$z`8t(Q-j<Q5i`{Tbi5{QzuoZr7t^%9zRI1uw*5smMtcp$j_A;byry~-G%>`mi;06Iad"
    "IbzPCe1sOv6Abq!T>Vz=r{Z4?M<9G(eLP@~A~k;nt3R~2UKh3bC_w4M=?$#qX}P+Q)c!QAc85DI+daPv@2C2iok95e&8qzy|Eu3D"
    "X29^zkG9QAD0`?cvIG9*$Li<3DErc9u7Z_s&hD_^RDPE|rVnqpi#9yBL;3gr3*&$Oy~2M#v;O-%{r~?TCK}-X03W9rOa"
)
_POW_DATA = _pow_zlib.decompress(_pow_base64.b85decode(_POW_DATA_B85))
_POW_MASK64 = (1 << 64) - 1

# Adapted from Bochs cpu/sse_rcp.cc, approximate_rcp.
# Copyright (c) 2003-2018 Stanislav Shwartsman.
# Licensed under GNU Lesser General Public License version 2 or later.
# https://github.com/bochs-emu/Bochs/blob/master/bochs/cpu/sse_rcp.cc
# The source's documented midpoint-reciprocal rule below generates exactly all
# 2048 entries of its rcp_table; no expected Java pow outputs are embedded.


def _pow_reciprocal(bits: int) -> int:
    """Java: HotSpot libmPow's SSE RCPPS, via Bochs approximate_rcp integer rule."""
    exponent = (bits >> 23) & 255
    fraction = bits & 0x7FFFFF
    sign = bits & 0x80000000
    if exponent == 0:
        # SSE treats denormal inputs as signed zero for RCPPS.
        return sign | 0x7F800000
    if exponent == 255:
        return bits | 0x400000 if fraction else sign
    out_exponent = 253 - exponent
    if out_exponent <= 0:
        return sign
    # The source approximates the bin midpoint 1.yyyyyyyyyyy1 (11 index
    # fraction bits) and rounds its reciprocal to 12 fractional bits.
    denominator = 4097 + 2 * (fraction >> 12)
    numerator = (8192 - denominator) * 4096
    table_value = 8 * ((2 * numerator + denominator) // (2 * denominator))
    return sign | (out_exponent << 23) | (table_value << 8)


def _pow_f64(x: int) -> float:
    return float(_pow_struct.unpack("<d", (x & _POW_MASK64).to_bytes(8, "little"))[0])


def _pow_b64(x: float) -> int:
    return int.from_bytes(_pow_struct.pack("<d", x), "little")


def _pow_f32(x: int) -> float:
    return float(_pow_struct.unpack("<f", (x & 0xFFFFFFFF).to_bytes(4, "little"))[0])


def _pow_b32(x: float) -> int:
    try:
        return int.from_bytes(_pow_struct.pack("<f", x), "little")
    except OverflowError:
        return 0x7F800000 if x > 0 else 0xFF800000


def _pow_signed(x: int, w: int) -> int:
    return (x & ((1 << (w - 1)) - 1)) - (x & (1 << (w - 1)))


def _pow_div(a: float, b: float) -> float:
    if b == 0:
        return (
            _pow_math.nan
            if a == 0
            else _pow_math.copysign(
                _pow_math.inf,
                a * b if a * b else _pow_math.copysign(1, a) * _pow_math.copysign(1, b),
            )
        )
    return a / b


def _java_pow(x: float, y: float) -> float:
    """Java: Math.pow, OpenJDK21 HotSpot libmPow including its SSE fast paths."""
    regs = {r: 0 for r in ("rax", "rcx", "rdx", "r8", "r9", "r10", "r11", "rsp")}
    regs["rsp"] = 1024
    vec = {f"xmm{i}": 0 for i in range(8)}
    vec["xmm0"] = _pow_b64(x)
    vec["xmm1"] = _pow_b64(y)
    mem = bytearray(4096)
    zf = sf = cf = of = False

    def address(a: _PowMemory) -> int:
        _, base, index, scale, offset = a
        b = regs[base] if isinstance(base, str) else base
        ind = regs[index] if isinstance(index, str) else index
        return b + ind * scale + offset

    def rd(a: _PowArg | None, w: int) -> int:
        assert a is not None
        if isinstance(a, tuple):
            off = address(a)
            v = _POW_DATA if off >= 65536 else mem
            return int.from_bytes(v[off : off + w // 8], "little")
        if isinstance(a, str):
            return (vec[a] if a.startswith("xmm") else regs[a]) & ((1 << w) - 1)
        return a & ((1 << w) - 1)

    def wr(a: _PowArg, v: int, w: int, keep: bool = False) -> None:
        mask = (1 << w) - 1
        v &= mask
        if isinstance(a, tuple):
            off = address(a)
            mem[off : off + w // 8] = v.to_bytes(w // 8, "little")
            return
        assert isinstance(a, str)
        target = vec if a.startswith("xmm") else regs
        target[a] = (target[a] & ~mask) | v if keep else v

    def fl(v: int, w: int, c: bool = False, o: bool = False) -> None:
        nonlocal zf, sf, cf, of
        zf = (v & ((1 << w) - 1)) == 0
        sf = bool(v & (1 << (w - 1)))
        cf = c
        of = o

    ip = 0
    steps = 0
    while ip < len(_POW_OPS):
        steps += 1
        if steps > 2000:
            raise RuntimeError("loop")
        op, a = _POW_OPS[ip]
        ip += 1
        if op == "ret":
            return _pow_f64(vec["xmm0"])
        if op == "jmp":
            ip = cast(int, a[0])
            continue
        if op in ("jcc", "jccb"):
            cond = cast(str, a[0])
            yes = {
                "equal": zf,
                "notEqual": not zf,
                "aboveEqual": not cf,
                "belowEqual": cf or zf,
                "above": not cf and not zf,
                "below": cf,
                "less": sf != of,
                "lessEqual": zf or sf != of,
            }[cond]
            if yes:
                ip = cast(int, a[1])
            continue
        d = a[0]
        src = a[1] if len(a) > 1 else None
        if op == "lea":
            wr(d, cast(int, src), 64)
            continue
        if op in (
            "movl",
            "mov64",
            "movw",
            "movsd",
            "movdq",
            "movq",
            "movdqu",
            "movdl",
            "movapd",
        ):
            w = {
                "movl": 32,
                "mov64": 64,
                "movw": 16,
                "movsd": 64,
                "movdq": 64,
                "movq": 64,
                "movdqu": 128,
                "movdl": 32,
                "movapd": 128,
            }[op]
            wr(d, rd(src, w), w, op == "movw")
            continue
        if op == "pextrw":
            wr(d, rd(src, 128) >> (16 * cast(int, a[2])), 32)
            continue
        if op == "pinsrw":
            n = cast(int, a[2]) * 16
            wr(d, (rd(d, 128) & ~(65535 << n)) | ((rd(src, 16) & 65535) << n), 128)
            continue
        if op in ("psllq", "psrlq", "psrld"):
            w = 32 if op == "psrld" else 64
            n = cast(int, src)
            v = rd(d, 128)
            out = 0
            for k in range(128 // w):
                lane = (v >> (w * k)) & ((1 << w) - 1)
                lane = lane << n if op == "psllq" else lane >> n
                out |= (lane & ((1 << w) - 1)) << (w * k)
            wr(d, out, 128)
            continue
        if op == "pshufd":
            v = rd(src, 128)
            out = 0
            for k in range(4):
                out |= ((v >> (32 * ((cast(int, a[2]) >> (2 * k)) & 3))) & 0xFFFFFFFF) << (32 * k)
            wr(d, out, 128)
            continue
        if op == "unpcklpd":
            wr(d, rd(d, 64) | (rd(src, 64) << 64), 128)
            continue
        if op in ("pand", "por", "xorpd"):
            left, right = rd(d, 128), rd(src, 128)
            bits = left & right if op == "pand" else left | right if op == "por" else left ^ right
            wr(d, bits, 128)
            continue
        if op in ("paddd", "paddq"):
            w = 32 if op == "paddd" else 64
            v = 0
            mask = (1 << w) - 1
            for k in range(128 // w):
                v |= (((rd(d, 128) >> (k * w)) + (rd(src, 128) >> (k * w))) & mask) << (k * w)
            wr(d, v, 128)
            continue
        if op in (
            "addsd",
            "subsd",
            "mulsd",
            "divsd",
            "addpd",
            "mulpd",
            "mulss",
            "sqrtsd",
        ):
            w = 32 if op == "mulss" else 64
            v = rd(d, 128)
            rv = rd(src, 128)
            mask = (1 << w) - 1
            for k in range(2 if op in ("addpd", "mulpd") else 1):
                decode = _pow_f32 if w == 32 else _pow_f64
                encode = _pow_b32 if w == 32 else _pow_b64
                left_float, right_float = decode(v >> (k * w)), decode(rv >> (k * w))
                if op.startswith("add"):
                    out_float = left_float + right_float
                elif op.startswith("sub"):
                    out_float = left_float - right_float
                elif op.startswith("mul"):
                    out_float = left_float * right_float
                elif op == "divsd":
                    out_float = _pow_div(left_float, right_float)
                else:
                    out_float = _pow_math.sqrt(right_float) if right_float >= 0 else _pow_math.nan
                v = (v & ~(mask << (k * w))) | (encode(out_float) << (k * w))
            wr(d, v, 128)
            continue
        if op == "cvtsi2sdl":
            wr(d, _pow_b64(float(_pow_signed(rd(src, 32), 32))), 64, True)
            continue
        if op == "rcpps":
            out = 0
            for k in range(4):
                out |= _pow_reciprocal(rd(src, 128) >> (k * 32) & 0xFFFFFFFF) << (k * 32)
            wr(d, out, 128)
            continue
        if op == "bsrl":
            v = rd(src, 32)
            zf = v == 0
            if v:
                wr(d, v.bit_length() - 1, 32)
            continue
        if op in ("shll", "sarl", "shrl", "shlq"):
            w = 64 if op == "shlq" else 32
            n = (cast(int, src) if src is not None else rd("rcx", 32)) & (w - 1)
            left = rd(d, w)
            if n:
                if op in ("shll", "shlq"):
                    out = left << n
                    c = bool((left >> (w - n)) & 1)
                elif op == "sarl":
                    out = _pow_signed(left, w) >> n
                    c = bool((left >> (n - 1)) & 1)
                else:
                    out = left >> n
                    c = bool((left >> (n - 1)) & 1)
                wr(d, out, w)
                fl(out, w, c)
            continue
        if op in (
            "addl",
            "subl",
            "andl",
            "xorl",
            "orl",
            "cmpl",
            "testl",
            "cmp64",
            "addq",
            "subq",
        ):
            w = 64 if op in ("cmp64", "addq", "subq") else 32
            left, right = rd(d, w), rd(src, w)
            mask = (1 << w) - 1
            if op in ("addl", "addq"):
                v = left + right
                c = v > mask
                o = bool((~(left ^ right) & (left ^ v)) & (1 << (w - 1)))
            elif op in ("subl", "cmpl", "cmp64", "subq"):
                v = left - right
                c = left < right
                o = bool(((left ^ right) & (left ^ v)) & (1 << (w - 1)))
            else:
                v = (
                    left & right
                    if op in ("andl", "testl")
                    else left ^ right
                    if op == "xorl"
                    else left | right
                )
                c = o = False
            fl(v, w, c, o)
            if op not in ("cmpl", "cmp64", "testl"):
                wr(d, v, w)
            continue
        raise NotImplementedError((ip - 1, op, a))
    raise RuntimeError("no return")
