"""Java: org.mitre.synthea.world.concepts.GrowthChart."""

from __future__ import annotations

import base64 as _fast_base64
import json
import math
import struct as _fast_struct
import zlib as _fast_zlib
from enum import StrEnum
from functools import lru_cache
from typing import TYPE_CHECKING

from synthea.resources import read_resource

if TYPE_CHECKING:
    from synthea.world.concepts.growth_chart_entry import GrowthChartEntry


class ChartType(StrEnum):
    """Java: GrowthChart.ChartType."""

    HEIGHT = "HEIGHT"
    WEIGHT = "WEIGHT"
    BMI = "BMI"
    HEAD = "HEAD"


class GrowthChart:
    """Java: org.mitre.synthea.world.concepts.GrowthChart."""

    def __init__(
        self, chart_type: ChartType, raw_chart: dict[str, dict[str, dict[str, str]]]
    ) -> None:
        """Java: GrowthChart#GrowthChart."""
        from synthea.world.concepts.growth_chart_entry import GrowthChartEntry

        self.chart_type: ChartType = chart_type
        self.male_entries: dict[int, GrowthChartEntry] = {
            int(age): GrowthChartEntry(float(v["l"]), float(v["m"]), float(v["s"]))
            for age, v in raw_chart["M"].items()
        }
        self.female_entries: dict[int, GrowthChartEntry] = {
            int(age): GrowthChartEntry(float(v["l"]), float(v["m"]), float(v["s"]))
            for age, v in raw_chart["F"].items()
        }

    def look_up(self, age_in_months: int, gender: str, percentile: float) -> float:
        """Java: GrowthChart#lookUp."""
        entries = self.male_entries if gender == "M" else self.female_entries
        if age_in_months not in entries:
            raise RuntimeError(
                f'GrowthChart "{self.chart_type}" does not have data for '
                f"ageInMonths={age_in_months}, gender={gender}, percentile={percentile}"
            )
        return entries[age_in_months].look_up(percentile)

    def percentile_for(self, age_in_months: int, gender: str, value: float) -> float:
        """Java: GrowthChart#percentileFor."""
        entries = self.male_entries if gender == "M" else self.female_entries
        return entries[age_in_months].percentile_for_value(value)

    @staticmethod
    def calculate_z_score(percentile: float) -> float:
        """Java: GrowthChart#calculateZScore."""
        if percentile >= 1.0:
            percentile = 0.999
        elif percentile <= 0.0:
            percentile = 0.001
        return -1 * math.sqrt(2) * _erfc_inv(2 * percentile)

    @staticmethod
    def zscore_to_percentile(zscore: float) -> float:
        """Java: GrowthChart#zscoreToPercentile."""
        return _normal_cdf(zscore)

    @staticmethod
    def load_charts() -> dict[ChartType, GrowthChart]:
        """Java: GrowthChart#loadCharts."""
        raw = json.loads(read_resource("cdc_growth_charts.json"))
        return {t: GrowthChart(t, raw[t.lower()]) for t in ChartType}


setattr(GrowthChart, "ChartType", ChartType)  # noqa: B010


# Algorithms and lookup tables adapted from Apache Commons Math 3.6.1.
# Copyright The Apache Software Foundation. Licensed under the Apache License,
# Version 2.0: https://www.apache.org/licenses/LICENSE-2.0
# Source: org/apache/commons/math3/util/FastMath{,LiteralArrays}.java
# FastMath.java SHA-256: 4c10f6c5a108a9c50fdf825bde0c4066e7db315c629c1cf80651bfd38a79fe30
# Deterministic table extraction: extract_tables.py (big-endian binary64,
# zlib level 9, base85). Tables are upstream data, not expected test outputs.
# FastMathLiteralArrays.java
# SHA-256: ea5b9dcdb95cde2105334a8d5db5fa803f08c6c6ef4fe1c6f53ca9507561894c

_FAST_TABLE_DATA = (
    "c-riG<y%)x)Gpm1-QC^Y-3`*+-6cqhNJ%OZib$#;AT1(-NGl>B4bmZvC@84s-Rrr|UvSRHmoN8queE0OkJ)=x&7h$C_ZNThzxe-x"
    "C^&C7oe-oNs#Qi%n5Q1(8t07(2-+{W^dK0fD-HUL{1>1vf0GILDk=l;vk@QQcFKLgf4|a@ai|oX)yOzhfmA=>>LfG3ZM6u1hos#="
    "o`aeu@*emTCQ{(-8j^sY%3dPVp>D=$fc}r9J;Kq*=E;zG(0DIZ5IZ#0>*s)0dwn1eI*JE=2jec_W9?6Xt*Uon{D(~u;Ophzfd6jP"
    "M&?H+Wy1jEu1-egL09ex0&elX5V1!OI9WsN(Qji%gZ|;YZICzn*?@e+gBkeh@ngUX7ffV42665NAm{Dth#iJv$rhmbM|{K%!%yQT"
    ";4MjKuq&n?K<3AI**yUAAw~_r71w!?|J3Y75R*uA4w(m&Jzoj9+|NTmGn9XbJ*M}R6fz%X;@wEV2Me%Xn2nM~fCD%SV83+Q0eEIZ"
    "hRCt-pUEN|i}eGn6P8S72r?ea#I6Z>9+qd}Iq(ErHL$xs`ULD=JWd4uo+SnNf}I2K(+5A1aoD&T;RwfO;SU2YW$6KE^vVmF58FMP"
    "1TfYBo{OEo`vCN{#FoI{x#<I+{igtUeDxZ!$HAsd2V`<qMdrtmFylq+ar7@?{cv2HQ~{&=*+HKtA_DmI)evlho{y=(r>9-P?g)<r"
    "k>g@g?IIkPzE%O5A6G0U738|n?*N_uR)Rb#oE&&g=`3J%!6A(6ZvG7VsU-uD@7vx(I3Bu&JEF&<6%j<9izo7-61cVqBj}xio`F2V"
    "iWeD&m*tQIyt2X!?79esK|XnH4*2elC!)tkEfGREKGne%aADO;#13DRmJFE}-vN&aFwFZB^cmf=faUXRfUnAY06+Vv!93fw@LmW|"
    "C`JJ(7M~;Y5eT%^09O}L1#TM*Zh|1BIu0<+S^}Ae;EBvvuxt0O1o@{4G2okz_kjO#qe3_#*)L8&K8`qK9HDARE%JOqYf{(;gu!@d"
    "fOoj>gWcmBL%>^Ir+|MX^+)C-T<@&``R{pRgcFe}c>{8Pq($tAl;`316ItxYBl8mlvYLYYHaENvqKCaz$atdW^j?sUWQPK-5wya%"
    "i&PN=uMyXN0pxsI0H`=Rj*PozeozAF7u*f<Tjt?_#TwPf{MTO2-$mxTHl&UPxDuNL@}J&i$T(u62t~x6n7ug+krT_awjg%IW{ht^"
    "?tKOG5GOu80eK-x5n!Vc_-o<;K5M{bmjC2uH;#~bN${uc0J83uB6<>;mSEr}k??*<Jm2g9PhhnNe*Xa8C&`PCD`5X#1rPYb9Z}Gq"
    "wvr(Bq`3YVh@O;1%L37pO2r%l8tst+x;K6XyV#g($T-q_IPU;!Wm`f1E|C&&j?)3`PpHfgB*T`iN9@R$@|=N7gk=CX;Nbx7`k4xO"
    "E?M*uKFIS7;Cmr^x^felkF00=3&^K`vw{7QYz>0sn9_%U^s|hBV#U~qJ-KeB1aKGHPslj(s1iG5KJuK7MbKAw>Vmv`eFbpp5BM|k"
    "{W}+ko&w!92jLX7Hn5*5M0UUrQfOQJ0l8DUJMf4YcHmiA@VhB0`<?)HNxwv%M=>eT2zK9ye;{_0sBPVdo|2l(7SU4*+XVt@%GZJ1"
    "L52f(SlSWrjBlF2%P+vMQob6x1N`&t6l7k??eTELjtWKa7s9D1{;mNR*o62^rEa_g-1cD`@Q}U+;Asi#z@L~;18>jL1wM|33VgHo"
    "J@Oo?KY26=Qj=5r0P-1K0jg$0zCdj)iwQiKy&ic!^&S0bkUy>^1m1ev81SRg5y;n9?g3t6P$T1LNNs-sa(_QS>}ZsK5FmOQO9E=Z"
    "K(lKgzpaxD{NdqK<oD4uKeGZHd4&z~HSQn4FX|s4NK4!gA3QDR2SPx_D@??W_Bs*l2U@>Ub!1-JTOsWrFAjjXLi_S(0?3Da(15Qz"
    "Fa`XX*@_??QPn;&o{oKT0Z`uXEy&H}A&;W-;V=hGd|v?aLQZ~UKDtJ4X|NwKgms}?HhvFyR&<5P=?PHa`=@8amO<q7GK-M6(VOH$"
    "yr=hECk1(e++&az5JOz2e{luzi~hY+H|Q6d;62ixPC)*`fP3#VV#mPZ;sRW%tO>X=5#&P*?i2lhvCkxs=P=ykhIqwL>uwJCu9Oh$"
    "=M1`lpNNtp_Ket$kmoQm^?gL<Wt1pjLG+9U7NfvjkLiKO&`5w?o{uSvdxq@~ycbO$aE1~5IOCCTIx>z4(+1)O69c9OV$USj(T3PD"
    ">3-Y=?jpqnc2T{nV3#wA3;OD%W#Dhg<w5_2aRTi3Tgnm6jGp)n;mowR0)dNSqyyKEg>`3ks)Ti8jwrnjJnPLW@X8G~u<LUB3OK0;"
    "`-u6QOdn#$f;w>nc`ggJ41BjN!Vv_B9gC(T_$?L(uW+yndrk><nH0YOD=4W!|LS-H@N?N2;P#I<h&?Ncwh=NPD<z8wV$Ui_2Kg|n"
    "dJy<UR@=cNz>rn&!>nmf!OyWi3A_M#dowRGAL}?BF~~R9CjtNTxFK>jaw&)tY<$u1-LR?F6(i%=tetNG1}i0l{!XwF;N!(Iz}6a6"
    "<ae=s^nV4o{txm;wo5@*WFB_XDA-TzJhXp+t6Y14%*Spi4EumRFd6ne`)!{YuzN)J9hsNCd59VGBWsJGU(<lRjs4<_9Ad{oyds3y"
    "ac~|%9Oh8s2mi-$UC12JZ<GYF=eU*21N!1ZF5pe1uwOWaa%5rr%1b?v|7?W)%}MkH@_kPBvj{}bDIWuQ2B(?L2*`a5A^+q|T!DOy"
    "vrz9h=o^zDkK`N(f_TBXoB;cl^Q;r{SS|uS@Dp5Y9O%GhG2wl1nbf}q?u8Qxm~b5jnTM-D^bzRm`EG#xeFEg6TnkH8pg%ntM>scb"
    "*AimK%@SLL*l|nsgFojs=7M<0?S2ON0e9>S<e%L4v>>i<*XDp9;ePj86y$T^)?jy{4|N3(_AQ88JWM|zui%krhu_a*klX?2b`9b<"
    "PmJ0V(C6LZgmKRVAA-D>{s3@B71o#M=;14594}@}J|Kf=Ga}~|n}Pg_SNHrYa2K;$;88mj$h^Ec2T;E9)}TIzac|YvLH<Q)4ea+<"
    "^AJ5BdKu(#e6)4Ph@MZBxf{{*X;(nr$mi5;2^i4}`-v~>5CyOb1L{@2u3S^lPkMg?`8Su(2<JyVbVTOmr*=38E}Z?JTr(*N(4p`e"
    "V$UBo5(svgDkmVX5c>t#3E>ij|8rL+=y&L#juSv}{(#5@DAj%f7gQqzuAT$`r-1EuKV+al$lphRY2&{EpJYIs5@?@Q1G{l?Ef}|j"
    "1@Tef&*4u*E=X<(`$3Se>K&l!FvMX&>oi5s2iw4Y7Q9mcdADF0wlXrmVCxXnt%4s*MnJy71nVStX$5(o5b1q*-$Fd9;2(ulc=eHa"
    "ge=XY00UbCKz}<E;;PUio!em7ybX1L&?v!o;A_r*ka>kJuE5_56aNN(Bg{nx-?y-mJ$zrn*NtOA?{@)tmGG?w_+7%qy-*(sHwnVN"
    "6CP@Vd_#C;6yCS+&q=6HMXq7-19DKnx{1iw!2BX+H^Bdj_(TRF_9BT_;IBjqL(o9p`0yRr4cvnlD6-rD`&#5|z5zi|0xK*;F3R>_"
    "{Us_ZunF8`#2fTpf{^!$CIl3Lyx_VWGOuX84Se^a@5|o6xJ6ub;NJ-$E{Nf7f}av&Dg2F$7nAx1b)J~9GJIEJ9#n?F<FFuK6ual?"
    "2lCq2u-;<tW?{X><{pWG{=|zML2>M-!H8U(nQRalFD@~+4`|Q?`Lej1U?*TqfDy>^D&cpCKeNCF?3HRm<`<vwXaW7vm?VM{n2*E}"
    "xdelg7jUtku)Y#{tgyZkE<v^+zi|z|8;M+O*yj>89QA;2!{NJ>_~Oh7`U9dtWSk`WTLDBaNju$y$R$M;m;kkh|AO9W7WzDr5u5fP"
    "&t~*R=98@AfcPcZ)r|)@nQ92~Z<$Ppy%ZW=Fv6v%Z!-W2KZE!orC9}exRk>n#2=}!Z<nCY41nJuRbdK#S*lYN{vWB&v&O)8lrIr`"
    "X_OdPUujAY@XOMIA%2LRw0h$r$nBT}KpsjDepWi|7sOrZC)MEprQ82J06uO2eqMTu8~mE|Uxo?fIWpvtP(R7=ea1!fGOF9)M`WyD"
    "N`pK&yaDh|C%jLYGG<G#YlSi#MdsrO8}JRqc)-hBZ;|n`q)p(@WqG`(kmty%Xz&4AM*RhS;5Nij+1vFr$UL%-BJF{<U?~BPO6h^!"
    "S{&rBvcK4*5R@aK5Jcvc<C5w}?BtZPU_Ion2QL8k=ZFP<Ypeu#@m?+1H|aTnd}s;&U%8ddcHlqHRS>=WHOV&!m*<d#d{AC~DgoqX"
    "5AuNflq~}$QA58-zOWGdqkLmqAMk;8c>nUtD`+4;yEI3*0ztAn!WGz@Spj7&pbk_p*-{1cG6VmokdO-bzd}J2^c589(;<#3yzhm5"
    "qOd5z4R+u8px>y7N7x9+(gOZiQJNUykfO1T3u3S6Ap>=nVw{96*xkDWenPQ!YY^n`eqzG7xqf}XlUtDAC}DquJX498{}i~y6$@go"
    "WUvbRK*`Mz;+axR5wvxc@_Mg>{j*s3JxaZ%5NDKTGAv;H@qg`NWz4sD$arOjEH^~2EKacrsHdNU*eSc*l?MF{NvNBZb6KIUrd*=~"
    "aZ~wi4F%wrq(?CBKpy;?3i>kmLlrs{sGC$ot?PhmAAdmXRGd!t03&h5L7!~|??I*Nzy7C6*B<OYmC0)8&#HWDeSz4kqH%&hR;8|m"
    "?^;#3ZxXRn)f|SrM%Cd0`U9%r_?=*vSqyPPwIT?<3)N2F2;iU3lwkah$9IIQq1;ylq)dapnVMiZ1)^6|{|t6&c6wqU50!;Dtd`CS"
    "b)4FhchFZ*>tN#mKJE#5p4yfke7|ac^&xLpCx76HaCN>b=%=fzVL;ujZaoL_NIf_g1MtoY^!3!sWD1aZ)Y}N5udDv?q95cN4#L1M"
    ">!GgGApP_g+WS1Y4-vhFijz1pPQ&t17wCfs5<!1^92ew|s-T~z(ZW#(eAF4<x5iot^ouoq>E<9@lSF7A8L!D@#{gXE?F2GT^LoBN"
    "VyEeE2L4p@)&b<Lnk5wDpl|X*2l+6DF5oH(FN{B@gZ`n`HP2$iPK(15zGp23RH)Ci%-WzItK~BS{e7(@@nyimZiru6jpI<yYYi+w"
    "{h{@h*aG+udVU1830~qNa&5NwC_vc+dO%Y&Ezo;K!@kl^D2INfc0oxz@cK?H!1t@k$n&%posD7KcOCfsI(U+Bo}t4st^g=433Y>x"
    "ap)Cdr{iG<b-GTR8^l4Kdo?hxP913&U>{jC@;sfng9^ZtQixZ&*r)J*beT0_zvxObW`Nv~SQMF0*DZh!<T39d&(+OaehK)jsu1+O"
    "{zJfL8lkVQdrSlMryk}i1u~BwLl^X$^~5D$o%Hk~q0g@8@>~t@h6B|1dbtX=z-s~=!T#+mybrxEl{%n5@PU1(kN!s(k?Yg({zl~b"
    "q7l%K($}Gy0lhOJ^#AoE1=Inv6QHlBU*!dPh5j3A17v>v$$sd^>VNwhi^vVo)F93nP)|Vr&Omq>`iuse`_Q*CaO4KRVi3*`{=*=1"
    "5Y8J6Dzcz|YtVTQzDt7%VjHmAxeIxPAxZ<hXG6*tupbQtCm@a*s-H{)w~K^4(=gNu@(IIqUFaVfK3V2LewSf~Hk`W{jwitXXSfvr"
    "e%|o!O%FtFMBZM3$c^~9-2l~CAA;NlbsMoW3a*1X+9(wh-k(vK=@sbPgdpx3jd6irHrj|I1-zVxzJ@XB0pu0NJg=Z0GFFN4MC^?%"
    "-?ab+ag+hxJ{1IfG`R)Xq5=IE<I&7M7{Asr2jhQ*a3g3!qC17iO}G*uZ!l3hxs8l7x!wxvWa6I)`@<xe;1ghpvLx6wB}3o9WS9^B"
    "50h2eK^S+g1btl7YlZMUQ;sO`o2CjvkcXL?eS!CC>T?F`Y?@@^09d$r3$Sqy>JQU_ztHzL{i+Op()5P{#2Yh$C8!(B*dF~s?9F7K"
    "!FO+F$_RCbnO7OaF|&j&@Ec|Y-4IvJ>c7Exh*>`x#1*r}yO4LAefNw(xH+C9)N$r4`_OMNm$uzO?9GkuLY`sn5#IoIardB}H@`Os"
    "@5{VS5x#fxJ`wPb=JS+ro@Rd13FkN0aj0bgnH^z&Uzb#Yyz08462yV)ZdsJTV~+L!^RDDT{_G><qt|=Wp#Oe-=8Goav8WOvx4=S&"
    "^F<4WJ$N4$;^xrjwa_bv{<Ve6U<}A_q~HVQT0tIYQIik#r9}@WoIhB682~?QaZm{7T9z2}(a7(xq`MC5VJVsqb)BV-66D>M&fFZp"
    "BTb;sYnlBL&Mz#h(%`(s@{PtU=qEP{0rzmT5WN+eBdnhl^~D7uw-UYp|7oQ~+ymUv8uDPPa056;v&uY!b1<ul7m#OJb#_BNX*IzQ"
    "{Rpd_W{8*8D8tYPv!)z>1}KCE`IfZ?DV)n%+f_oJ(mFH({IGR;7$e}5->@&NI|3kYvK}vf0l1Z`4)VWs@c-J7&w}5v;Wv*$#@VPT"
    "!+W-|;f45S6Fdax05++7L||9u2mM2vHq&gd8?)F1`9>-1W1A~X_<wE5@L^tCo>e%Hu~jL6eygqJHtbv5AjNIqDdcH@rD)K<wrz1+"
    "f^nnm>tMGw4gSaWR}s|Fb|mf)x9zy9V14bBN#LB^?)r=nVrS>y0Ck#OGC#x<yAmJhkJ>dofqsVFuqm87+pS7u0iL_U@3Ox(0^hwo"
    "M{zt{7f`T!1>Ee69T{)$%Lx4@`=kKq|JoN3+ywp-6Z*sUgRI~m?7s#>U(^1F1H@woLVW0>I<R#$1DBnI_~T$I3+FlxUIVay9TKL4"
    "z^-5o&J7(JXdx~;^s_;q)?u*|`YsONZ$n+-h?ffeW=B>W@Q04lNs!Mv8rMKS%+aHK8?kqcdk_5x$9p?=Ag}Xz2zGr&;I|#;m52dP"
    "rXl}w!cjOuxD)dY=tnt8y1}`KlVLy!aJPEM1D$Tt!E>DQY0dzj{bWVvb?U8z{<_o5@B4tqde9ee#^M-3#yK<6!g-Oico_80o%KFK"
    "ee3M90q1khH(o$r&N(+U4zQ;E46uh0`smJIcEEo+9}GZzaKVs+^D7s+1c>u4qK!_-{4P2kP+z(@t3lr65*Y#aG+eUR!QZ%4)j9*d"
    "359yhWeOeMqsyMyDl)Gt+D*78;7Y>`>*Fdy2L9buOC0K4SI6{7;NgLA-sF0h1>UD?#Ru@iuAMv34|JW-p#c33e0C^qDC^)i+$hiB"
    "ce)9QP9h374Ka8hZg%6)_j3!q4|%3r`Xe~^ax16Qgz+8sMPS@`3*2*Y+iHRP9BzLXSrNHA`2~Du?)(XmC%daTKpy69W0sHDy9aMz"
    "0HzwlbKJ|ITtjhh3r__5u@vYJxo>nszUzJ^0_UtAWZbYW9=v$auk%o8GDOCCSP_E%@(8km^8=3*DH`N?9;G5s*L$=i4+9@v*Fxs="
    "So;qBS&v`u;9i0!Ng~ugo?IgkFFlocp^*2y{tNOlPyeMl#NIPm56;g$OYV<=zNs7f5uU@*@SS+B8vlpqsZeivUAu(yB`=OH=wEm#"
    "q&Fhtyv)fUetY@qK%dPkDINTmSCJU3o7YQb7vwo!gPQ+<f31M`;PoSZ50QHlN<$v+&9(sR?k)QV>SJ$HOZdIsUI%rcPdJ8q2Hp>_"
    "On^7&!MUt=zq%mc;x_b=yuVlaBItwH1of^DE4vpmuaERosGEF@dtU+f7=U`(C+<uc<o9u*@8nbW0Q#Xmeg1H+;4|+9d7#h93G5?Z"
    "9M=s*?#rAH_b+@U?+_v5d<{#X?(=mUgM7~SrWWjH-+ZZg&_8E{_4e)Ufqm^e%M5YF_t>2d(feU(Lp|xor~~oUPyF5lpx!UY>-=2N"
    "pbqf6F)a$1n+0`}U(FKK&3-*nQ1AFn<7EII{DAt&AH%jB8ShV53+J5vq8}kI_t(kt0(5qOex!e7F`Qfa=iotI=U?>^?xpy@c>=%N"
    "e~JzIIsSVNaJ~_MRs{FI0%)|L{}CV}0Qa;4w5%b&4{&@9>lYB71AU@^yGG!T11k35{Rg}zg>&G533s^15U`61`F$YDU#PzVsi>h|"
    "4HR;PI31{A4)uPZ-5>al0z;eo0n-PeZV4<Gg*rE|<29V029A$GUJ$r7%Le*?1aJ{0h=K;rC4%^0K)oEK77KM-kj>3u#4acV1@2`9"
    "rA9zMFQ}{x>WQGXLiim)V{QDvH<qEl8gymfi|}AFP3TVs^NI;0@?e!Q@bke|qL60=2L(f)A~?l*1$e0w^e=;3DtBPq2O>Cc30^0G"
    "K5Fo<Z{RmVNFJsl<3hNO;677`vbroXF2sTk;%rC&0ragyl6~R5hm`cdxm`%pBAg$G43~pn3|aMshEB-&3mHTnN=ya!8$vmjp{@&6"
    "=zx1kq2{7vAomTO2cA^35B5d2a848YQV#rO=%8;P*nORXdNlOM6Yz&&gdSFaY`>vT8z#q<hv>sh!{9p&^CpLLzOY1m@FQUlcp;94"
    "HQa=G!}{H$VEhs}+}8>F-Us_39B&cMlfzk+KOy$v(w|TfeYo)g#ItaZUC8gl<JqB46n>u<?w^F$^}#);@V-nH7&o5_c}Dmt5f#EC"
    "aMIyCJc9WJ)cFyT&%ysj7>>a?V}#ogoM%Ve425-w$iEKfL=n%m;CqPZU4Zu*F{=UhB_fXFpuZA{<!go5M>0m`BlAUyw?aM<sn5O$"
    "dRJ!XgGb)@TM3x^9Qt&TPtk(FuE!Xj6FDtF0Q`^*>We6h80f=9(M>-C6y1Y;8Ku+a4d{FW?ng#NzJ<PgR1RA)GEY?1Q2_8a<8ZDS"
    "HKhuD<EXtfLuB3?Xl-y`;Ra2>IiQF(%zr~G7WxY}91q~$#EtN#Xt2K<3w^>Hm3R=BZ@iWtg>e%}aKGioF1H?H7mZ3?j_9MQ<iT%5"
    "3*Cc#9IX)n_obrk`5<qI4xNBJDmwjy9<ba9{9bg&8q~$n<GU<?TbFRo6#Y*D&c|aYWU~;v82)+i_c3ZEaE~Fz2CkQ)#Dvg`0j55J"
    "{##60Cp$7vOj{TDnV7LH=tswF{Db%!bCu4G@S9}ru<kc`?chA*rphk#b#Gc(fj_?)lmYe2&6JyPj(W2+#}(u){gC(G{2&YWCvUC`"
    "{Wsrl(lbOKOVUA$@K|mNab$d~vOU!Au@;IDM`HuzV4Y%<Gm-#H_Q6laHvNKxCw6!Q@`~8i6zEsSo=@l?7)LBDg^Z8mM9D++aSGdT"
    "pC``T6!MEW-%_Z*<C6NB!LBH22KY-0$hYDKbKpEZZUr6c$+#bVkRQhr-h+O6JUb2CJBpVxB?q}_4)~dPZ@K^Ei5%dU;~yA89Tng3"
    "A_n<g@%<@qt{A_hDxmzo_p1Nj?`8k*{r3Ma2zR`h7Kh+YQlup0+L1y&a96qdaRPEz7Zs}+73oD_4Yckcz7DH7Fs=$YdiLgOKlvZI"
    "d`*`(5<@QYv5%3Qnx7;kawY)<yRs`+>3?c_90$w9s{e_h^gn&1?pULsyhE|^^_oFJO&l?|TKu0HK-lb_p&K;{hE)2RYP4DcYA5Rp"
    "(j<cfV)OT#Z$IRtsNQq<vPZLyLfzI}c~#zx5*bvcH0yLXA)Vlz`r#rGO40T>19^!K%3!+Z<G&gEDBW3_M9;;-QBLzW=k?B)Q3(V_"
    "Q3HPbN@OS%dWf0%BN3Ycn|Q7$9ThKO*@A{f3zff!akJW~2=%6MKo5rVC)B&NNw&|NT~G`0Mt;R6=%5a?KCC3Ff15a`yS}WN*_L>~"
    "Oxu5LBqRx=|Cc+8czhDtr%Za8$7g7gEX0ay<(o-VC)Wly2Pe@yigtdhjVmYF)@>O%O*5c9l<^uO*Zz=H)4}VGtMV(UDQxcHP3Nyk"
    "kE<#ka|+I(bwv=^rZ5_y?L?%^oBuezMK;DXxAZammQ3xrMqI$)Eg|J!FGAbRZyCGaDf$}EaLfBs$)zLl@~zBwcX4R5H*S>|=GOiD"
    "&U`C<l+sag7US0Bt<N*f^$fSxUL<nL&{p0$2$(7-vHW!F&xMMv=I3J!l;qU62TSZ2hAqi2RE9N^&9)*E2Ut*(UDM?mhw!?RZ7c+>"
    "<f%R+*M!c0`9AO(qmsrh^ZaTIW7z6<U(&0o<W>CV8(dHIFtO9ZCJx18G5)QZKWO_<cAJFMx7Qw35>r=&c;k?m<+ja`R0yt40cITQ"
    "@FUCNdCVjs9B;nf#M{r+dC_}viZR<50)9JW=iPo&B!|sy)q=V5rxI19r{nhcs9bJX=7$uf15}1Gv;!<b<*r$lp}7?CweFw%O`}-0"
    "4?B`V>awsrQtICO-8D@~9Lvw<VzR`_+u_#j*hxs~KB=)QudGdJ>N=FWZ5fWWPA*U@>!ybF)BSdOz|bN#T?ShJYZ4i(lZ}QqZ@Rg#"
    "Medc`mQ|75;r4afi!5Qi<GW~a*~un$C&Pz3jyIe2PJR~u_}3#1><nJ7DT$*7?E9{TIRdZkuqza(ILJw}?p#pi&V30qP9>#3iPkV="
    "#-UTIK0d-`P9==1J9Tde!_nnPSktzqP4#r3@;nWh$MLjNe)hzL4W~4ELU?147w7daePzo<xzu(otk%4ZXq-hQ<|c{X1gVECSZjEZ"
    "bE(^8bM;>ib#Pg5rg8+Rx6?4*<iyZin@`i$Xj*F57f5rvIk+=3#F3Wn`%}_`gBSNc7fGaR`WbGJr#+jL3|3lUX>+VqOdD<^%0ybb"
    "JayU`!PTS8VJ6(Ax%2oCF3fcHxT>JfeFy3Mg(%hj3sHEszer?*cVDNA$<H?|&V5V2dx2(&nOBdO_Pr#1ab6BDV<uE|>HZ_UF^ST;"
    "oPghW3knCxI4bUVhcBwgOrjanU#nazaokhG+gLRr#0YZEkTLM4O)nzLFrsNf(d9(P=NtQ$(XA();q*yC!yRQRBkxGhYO-x2qiO>0"
    "ZBpzP{AaDRQt73p88c@+)N37$_?Js#**^tR@c)W+tx?^NAz=KnvUi&^75{j}?IsJ#B!Nmqi2AdSPMQAxfotSDB?Pf1XqI_n4>J9y"
    "OxUXly$RB9xJc`As%18B6RdxK#+uo@AFn1^VnHwyFy$e3FrInFvmRSJ*F#9f;Jq^tg+<6m-o<hdy>(Zc!93Wce&KGQ0<Pb^J7IUt"
    "I@60e@?{B2^@CJyt7qPQQ1xK^JCXd|)E~KO73HXe<KCi&S!zs#YnV%SO|ni22OI7X1=Y6`?vwpMmmjpql3HdpLoxTwQcub<S(`e|"
    "@;ac=Ww@bE<eI?aC;f$pD2}5z<Tkx6QA+VEo}@`WqNW7bHzJ2xMALV_+&z(0%KG{`>EFi?Q=%V}38gQ?hKUaI#t#1wPG!r8$p#%t"
    "A6!#5l96^+p2@Z@%PwI0Nq;Ty#yu@8(e~^F`@of#Lo?acH#Yc668y5CQrS@HK6res{m$6O&wGa1Q=u^(U!T6rKDO!zPw&CZVN~P{"
    "DDS|}VcE3QFP0t7Q8oBERy8<6EI*!;`si^!aZK}E@O`@=;tU(Ff7*Z2iJxP3H>$Q><UHJ!kjTy9&gl-j^;6^fN8$sGMP(P-m&6x+"
    "wXM%pDRSxa(_EiPy~+7b?^J0S8cm|Q?HC(0HAWIALA<W~J(wh)kq=Yty%R}!)IOD_uNKL>3h{iC?*t@s<9a5KxE_;iUpYUPqQN4$"
    "njjn^7~Usk3jNnzu63W3zsZRWJ;sAnN3Q-N>-{3BnL^y_WRg?T=+mU@G^0|a_X+T7iAl0apBsOQKxI!N?YXo6_vQBz(y?zJC3_aP"
    "NDqy&F2lJ$lm6Z75NPX>A!EwyGP(2h7a4B@6aM1s6f&LXp)P?@*kqosEo>jH+$Rf*t)&byXC}+7VOP%<KO!r;EB6u0WsvOE(Pq2-"
    "gMG58&q;CfgI~$MX?V{uQYn$6mBzYEFddSU;$7W!E4d_>#Kt*U6KyBgQ12(=h$$pDHMwx{zn4pHUuORL2D&+U&T*L3(CAb0!do<o"
    "&A&&;n}4;ux)t+^{9}&%I-~vw`RA9!SUWw#<QGmgZP5)$6qq$h53qiUQ;0OLtFhc?qL3J_;p3(HPGPCElvBXRKoM5QZG~sgL6O>M"
    "e$+#jPw|xff@pn^oT5eG+W~d12gRFY-;H$qbBc|7sZN_qMHGAFQ$;)}MU-S%;SNa{9hCg-q<nU()|B#il?LA_uqm%Ew+o;yR!~}A"
    "61Frm+@Q>edhwg<zBgrw=^`z9fdXYS&uk|t3p?eo{U~a!qYvfI@weVeKME>z`F@vr_oq}edfSo20UK1j?x<Uex9(DD-+#q+m*g9j"
    "Ww?{d0Y4v=?{89*2V<yIslKbWai-E#xx6kBijOy_N*;`kp5WzEjVSi8qW@{9`b?O_=1lpA>SsDfC`Ft!HJaQ|l6<QzH7nnljXowl"
    "wX*OcadsXBwWZq@@ji|Zb&#Kh2=A2!b*d`r?>_1K)LAz_4Ml0bp?-0zR;GH~fqL}(oIxtXg?hE?<|plBQ|h1lTxqv2Flopy3U6#R"
    "3DB?`?4K}4YS2jRmq!}Px6!DcI#`vG;?e~0Yj4xA=+Y$MyInJUgGuwK-4gZSs+y+twod(nvIUyY?7w34-oK?;7|P;TSi4ShmJv=r"
    "%GgAEEm8f?`y+c=ZgPIMXMIGpBI0xc?DE63Cc&JTjMTNXL6pK~vt~-PLC0jFYQ?9td9+wv&YnuN&tDHbjYauO`^MZ~Vb`;l_Cu=U"
    "D;mq^w5KoBMTLmb=+J+JY7#$Hq2vCOwluEDPRGijZ%)%0OQ&$2<4M=8P3In9_@1k&gD%$KGAGPNn=ZM1x>iv25nW}l+?L=17TwT+"
    "8|zz}db-uOi?`!<Kho`a?=o&By`aB#BYZg|&61w@<J-_8^b&gcyhMFDb#{8ax)Ghx+$Z!-Va&rCS2XnDWBj_yoh<ZsNX>7yzC@?5"
    "H{{8kvbUxm%*UrL$g-ke=;1XVqur-pAM3l#Xl2WQi_`XRKYNzpnx(~@-w6?e>?Y{~d8!SAR<#!)b6hopRm|0yf0qYC63Z#Q1m;_Y"
    "Y+|enUz`nwn!Mx(oc~f7+W9=_!=KqRj1tfgxZ`6ooH{n>4qiWF#OTTv=5sP<Bp!Hc+0UlJ$XDtftR%n7sQDD_>DS=_Mu)xM?!tOi"
    "jIo=<86%Q5j2WM(|2R1qlm^|tS1g9U!}xeJ<IVnZU1|Hx=(D4-?$QxD!Um?me8v@mI_jlarqX{mNEkUgi<wYEu_rUrb|16LG^IWv"
    "DPj_dHDRi(7kJE}`@{V7lkeleQ=+<0ITMewhSvWaK8<>udwChhWFgG-0>gigX217wr)}gekC7kKLbTG0eSeq7hpwx!DmzQe7z^Bg"
    "PB8qKg+9I%?h+hf7WXGh)#CnArWTe<V0<LaZ2Z!XEtEutIn;LHQwmX9SrOrS;9{g%nIk3Y&ZFBi%xP@Yq<8jOm_H{yDIvG5E*sgR"
    "bz-w=WL{Z(asScE_!HiF#>qz>OHZVuYB!~&$yn?%<QOoo=vX|TJ^6^)viu~{)03XAT94(?hMo6o&g3W08oegg4?jL>k)_7Z(H?s8"
    "tnk^rrkUU;$MF*`Z|`4Y`Kpw|)>-_O6?<Ar8uc1)x$M98C|7!0R;lNxcvh<ltmfO)hPi_F<@S`cO5z-W<rx!k)rr3LtWTbspMIu!"
    "!#c{A-&J4zhjk$$*K#otm338)?><?9VflGc`Pp}sk_!4eC-w$XC2YdonYkkcPb(zDI0vHlve^7&b<XvA7uarIABfZ|V64a_kYsuG"
    "hppn_4e}8=Y&EvlKQgN?@4l-Tw{{d|r{Jkrx)q<v#HLsAmcL2Zz(<!IcTRSaZCa{Q-o$N^2c52xA*DFNL9>fpXu#wg>$fy};GkAu"
    "Sh9R&q7`~dw#hnsh9mdge=j{N6GKB!FGsK{XWmS6GmuqP4!&FcG{MPJxtvo>`*JXtgYuv6J!<7?4h8O{#JOoS4we*=We)4GDwTe!"
    "yECoiRlzSK+9RL+<VbB(#Hy3&uBts2EI!hHSCtp0Ws&`Oieu?*HnkzCH^+9(NoUO?5>DK(x|g)1A=UH~jGk6r_?)Z-M&VI}l$=J{"
    "0T1P#=W$v|wQ0;HGI08vHk*4se9D>PsL@g-O2wJfu-IsN&RE^};`Sl^H)qcAe%+4(zdJYwRL!}Wi)X6OLZW$+itxE;2v@2#%gniW"
    "u8#;j>K)_~d9iAfTCBol@xrj=vSg{opOI@zoU58Ex#xFvcN7nooh;7i()KD>r8xQvx15-oj+$y+PkVl@Lq<<Fl-{p3`Eh8kW3UpR"
    "qR9T`Ia{~orsr4gp3xS6s-?@Du=}@$TO<<2RXl->+hg+UUuo(H?&N!l24RoTo<7u#DMF{Vep)Ut*b+@m_Oun#C9h|qihF>+o)e`H"
    "pZhF$!>ifA<r!}Lb3B3+5$@Lc;vWY*pPq^Pa4>0FKj6{Z71)TaqI{+*Mt*2O_Ul=^R<sEA;^SxcihX;72cmf1UTj)OX>IY;+o61N"
    "Ye3~W*g=~*NnPVP@~=zvy!Vb5&4=>0`LN=1zNRs0u_xR-zZoNKqpsud+A*Qeep!m-^}4kbFHG3>+*^rD)kbKTHzjZJX26p8^P&%z"
    "D#-?@yljf-wvX7xp3g6hby`k8;@ymGM#m3R;axshQ+x3yg^xMeAji=qtCn)wHdSM@i%*R}{3Ie>o6podJ^WwlAzudWmgA8Wd+oz$"
    "nM!W*Fuq%jy-!B!-q$`iSJL4762v#1?MIlt#aDZt#PPY_>n=Y=D1H_eWd=V5H^B`z!e@1YFFCea==1n(`L29R*82HfF!g^eaT@bS"
    "D-xIPX|>kn6-N@4)p_t&&S|<Ff7#}L7(I~uNAh>w82g<kiSpO$#vV757iN&vopS#<KQ9~>;H;|9YeAWLA?22E!^+26K)pBhrev4k"
    "3r{P{+Aeg77x6Js7~zv90+CqXK15!-F3|AFbSHG0{l%E*?%;`?l)&`I<!%3+6oGx*NI5rQRe|sF_Xn@I9qP&7{$@Bz?5yXzdT#L$"
    "t*hRUgoS@OxkJ#iprY{cl4rehJb7-52)>}#Ywq8sLJERq@76R_<KGBYm%iy#=yMTV%v)4tk{=e_%Ua71<-aL}N%&ckK!{ZE-%83a"
    "*=(T(Sq!v|OCmubHNV#Sy_CQPHzl-#=sWBU;bJY`WLcp?5u>ic?{*`F9x8@7QT<+SXiXNDR?%o`SXv?+L0j1n`qZ<>C~+m&NZ4Z*"
    "H#)&3Oc^}CvGDX=qj-3Y7rM()qY}SO`Ubj4qt^D$v|_xSaNzkrk6`!q#!SsS^HJ0^jZZr22NE^Yh2Pv(`(V$nAzVgxefIm2V&it>"
    "6FC=j6cH>jz9&YCcV6P{OZhOTAHU=)`B29g_CrK_%i!FXs$9hSgXP^#MPrdrwxW#RUc4gVuFoE2J4U~>-jQ=1?81FnZZ_lE+}JBp"
    "8?8op=cTpC$8Q|bhD^R91N(JX%F<g+bOC}hN{{!OcyXkb4EeH}RPfLw=rQR<Eo*NDOT;mVMjlW!i^dK$g^gpR>?MkbK5Ew_T)ear"
    "t!g<95))}{D!AZhO+KG#njOL2JzR@xI-lwyV0Gqbri)JAYGD`@WBr^@c5L=iOo1NH%2&rh%zoC0YM|+&*@=c)Sa`}n>~6YwsNao#"
    "vG|kW?YnusV%4Xw`zx30#cJRBVqVbMi0x4*wO^IWi5-`GArv=aYoQFWKf+x}ZDC1v8Fj485+~++JL^t*)?(xQvoD{hSUk`uW^&A-"
    "q9v5BBCI?KrzPh(dpFfj;+E)}ZRlDT6fN%~w9@94%39`7|7vyzYP6hT4_bX{s%gc3;rwA_@2&*>!yZ|Ic0CEIrReubs}CgjEzML1"
    "8B`?P)*9>@6#80qTHQn+y)uvp(qw0u#zt+;KWj(T+A?bW^h$36{qMcjQGVtIhUrm>uh092&E`TSwhsUOEqeD|68E?m&uQgWn*bWG"
    "2d&L5Nh4$JshxsRNs`N4g>np6$)ql(zciDJlEo7R^q=0cw3)fDC<V3nN;dHRbsYT@)i(bAekavUDarH7*wr!b=aQRwf-!XgpW8Xu"
    "8-)z#B&2u)?9vDixui@qc&K|1#M&Ks9ylplKWX=RzUOBoPbrm<7~ffg_D$;9oZh^B9i~*@<x_Qyc4Da+Lf^ka+Luzh`wZzu^t;md"
    "|DNJA-CvMqVYmDClb5=KOn^#mq4;$Ndvsuc7v>{r6DpM2q$jsKZdzDSh*&#HKf-LL_NONADC&~*dP*DK@v@`b_VwL|9SdID%@Y!+"
    "9fz@$Vp#(tGI&K+HWIz#(*JxY#F*JoWO#BTg@<s;UMVOa$5zOFk?|UEkk^iieHB{hn5ir*_9|Dq?}A=j@>Om9p6&~!npdxNt3Qt}"
    "3%wdn?^h7o)RftX!%>`JD3c}J&c2P;&CyBH->s+8)7;5lFr>%ig(|Dp_$baV->*{&#e$k|6;(ElN_%hbAigt*>dCEfqoK|x3^<ik"
    "mxG<%+U+Z>SrW2+lH%H?&m?7Mw%P(G2dm_;>c!9rXYu5iMx4z5MpV5PW@UO9pZ7yf*ZO#cHzwh=3C|ZNzB?SR^)*QQhL|W{2P;Sk"
    "_0=uCe$n(^Gvbbl+-=v(>ZfthuUkwG;@+t1%N_Wez53%9D~}TqSIic5&_(?(u{$axqKmIgenMzWQC?|6gPdHly36(hrr{2GN0-33"
    "UTX?#ynMn^^FDKWvwYR}5RWa4rY@gwl2KyD5c#1=C6!#9W%+FzuZM4ndb*}GcBTrvWZp2$k`10=Gj*ND8wK8=se8lnIPI}e^y@dG"
    "CxlZnT@G(<1{IcENs_z?m%<tu)Oq#h`CM&vz%x#T9Ocrcqwo3(AK0H|)fPQ?vovdAZnV?;=HF>u+Ipwrn}0C`g3R_>iZqX$?elUB"
    "y7iUg#GTmFy49*#aze^;|8KutF@n2(qPq6H`(|C5_9u~`ZWr9IDpg*}-MzE@HH9I0in~E#*-Rdnia&FDvZbCiD$&+2Jr86m>;5tL"
    "Fem!j;akGNTPGV|P?U^#@!l$4n^7`ZEd3jM$gPw-d9zrs3`Z%~XZX5=euUDKIQ$o1(Qmx%G5vCbcxOy$<tYlY4y&rt4uj6g!#^@g"
    "r=p3`&Q``fIC^f;62HBaIX{o%V2H@{u;CO^7?2kBXdiK-{vxC7iF$|;*Luyd=XS7iZV^GFaucr0P<lgq&%phA6^<74Jw0SJ0|!k7"
    "Ju8zrqfU9n$~%LoR&}n?DipIOa|+jTR1`A5`YoJ%P|+^<V0DRerDDF(fWbP3+MCe7igUV-(Oaq(Qbp;`(_1fanwHVt(_8W2Uy<{U"
    "mr94D$U|w*hbpH@RWw2>e|x{tieH~NwNoYO9)EvtgGg1HnZ#Pko#Y)Ko_zQpf*n;ogO$Nw+nw)jpth-Oy!Cn)xUjNGyAY*X-|;#;"
    "&G6y7UWxgZetdb=@l;jg$9GKMU7nwH7BwZR{$@?>^}(1{W6i?W+xzsjPnbjcQ^>oUeabr;{cI<5eWqp;WBIw7ec`#MR-dwB`pj82"
    "_qSq%`zndW3r_C8Q~OY4wl;d>L~W^G-a|)pSnXS8q9BcNT;I2`Y!^x!?)Owg7gm~)6z|3GyhOiNkgAJ^bve7Q+Q0W<7QUgOvZNkE"
    "7`PU9zVJSI>J+QaPEtLwChHA<ufF=L_i`Aa*tP1-DYvOmX}Hy={(O?265#B|x98n>C9={_tHYR_rAn*8ZAFg~;Q78^#!@3lg;=%U"
    "tZO&NgK$lQC!U>jePN~lwrh8rlHcq8w0&VS!s!%^#`n4vrNpKEGn5BMZ#&5QH~#Kw3nvC?5)p*$lrGn363bUcTBY?4NT%EioYf@L"
    ")Yc05pPzZGX%}-Ups<RrsY}y?F&v39z-&}QSoTv{GoQ^D+az0C^M#33aed^O=1}3?L}i~7&2`ZP@(Qj_EuxKIom286S`-~PodO%$"
    "TDZj2Txf?JT51aUuCIdk2kq;&yYC07X~j^{oz=aQ(2A53knE3D)+(gNwcllH8SILd%oriMKR9g`xGu1Zt2HsXiND~ht2MjLSL(r$"
    "tj$zn{7e6<q&9h&$-vh@hau7NwI2;MYeROcHHmjq?6f0V-AuQG0)`T+-4bWm-woBD5~3<9@M@P+q>Vb#bZTewln9fhtqkoaQ{a`E"
    "3u_-Oyu-nHV?T7Ud`B-^ZdQlCI`-Ou%lxn=apBpn=Ivo?-^HKbCYOif#~Q4K<ot&d+~c+e`sap=dSY&<k)i8!@5&vV46W(BD~SD7"
    "J7BIeTA6{Z(cz#o6OLp5$5>hCuda^45}UFvx@=IVPk_5F_l*SneaC)Xd%KZWYUm0hUR&?-%Y(OdQ--JYK1}0|BoJeZRi_&3<}HS|"
    "WHrZ)be_{T1vIaYO!Wt-KFeLvU7|P+(Rf`wit+IMS^+KID6wyFTg1|*k;T(@FXI-2^vov{>#rW*jJlSo-!4Qk*UNJ177aJUAN6}5"
    "F4k0QJQ^GG79;mF{%BV~h=@l~>FCsAa}N%+@aWIjdA|!I>Cvk;re#uf^$*-htgPu`cRwij*Y(Kq?&<T5IQ=tR+R>LayW60y7xW>a"
    "a^m)C_HX?RYnFb)>)Rh1+MWbt=dXPD_+Gd=fc%&Ks}NJ>u<uhJ{^EV%cYSfw0R7b?>+nFUkKAO&;vs=DAH_JCrkU9T4Q!pQt_6Bi"
    "eDu&XKd0>c_A%=F0Dj6-M}vZnw?BpYq76#$EivaW?izd`l*o=zs`z-j9CxOY;@IF*@t>U^+_Gc%9@q;FL;no99SX}u!hajeGTu1f"
    "N~{<&z<%&y6zANKa{TU;O<{sz>?@iSrT)FKj0XaxZ#h-QD%T>To5ZUO-(v-Mh+A+PE==DUF6g^&Sai*L)Q7Zk>@b0C2)}h@Y(jN7"
    "%(0Z)NO5Jgum<yuk-D0m$(B%*k;X$}#wUd<pKkt~YRb3LHY%KarI+#)-zcA>H*IM_`qLY+_IK>=m!B3}*~iH1#y_nax_s~WEcEGT"
    "WVc#z_^~ks$pgZ&T8?qD2ql@gOYw0&KW&9?Vcf=^qB7|8PI}|vDR`Ql_ehP?9hcZse`Ak3H%@HyQYMUd22cFs8M!d-kH_M~l*=*x"
    "qEzltFeWzsMHZ7@p(Mfhr}PX_grS{@G-Yrd2Y;FIuc_#U_3*OKx&^hvd8NmnJyl1VcaxMqr-a=(ebD{tb2$zdk%il*&z&@T)-k7c"
    "pW6cFTk3G#KJS*%i*gQgPGCn}-RP=(Zc1*)O_J65;`8=_5FYb|^n~2Gr2lEdz0ap*ZNFc#_e=!(#u=aKr<-PJzVXc+7n-QW$R}~f"
    "xj$ifk09pn{W8<JTw5b_?SB&sq6xzX_64Tr`vj`lQT~(UpJ<K#-j$mqCnZvzrJk77>iJo-Q9e9rfc1q@B#>azvz=zXXJ>2Dl||;?"
    "K#`A`k_uLdd9U(hlj~iq{xP-5PpS86q}wITb`+l$t^Qq`{QK*rqZi8H6cJW-EUA_16o14=ru74ZDg9}`=4*ys<|>s!D*q(-r`(Qq"
    "XjNLDn`dF+hhVJnm>XovrlZcSOjY1}pZB#+n}0B^Zo}yHo7#LoV)m?zd#ZIXO`KBX?-zp250MouDc1#-2*fs(o?q8A;P|KM6ZORr"
    "`(yva(fuzT9sOmtn<>|Wcw)oo-MX&dT1))JDIxOZG24A%<t(l1eVk>~OV_S_IY2Yn&uTmPvdI{Bq}p+H{hK1OL)HqZ1rJ8Y)!Jcz"
    "g>ZS2RyZBEg*inNnVt%ng-iOS8}qvb3ws{AJTly_>4d-2f_;pq(;iQs&a_f7TlA>(-Eq}Quqb0BI-VYinLZ^u>(KqXIsK!(^e}^&"
    "c82HW8ZL^)+>C7NnM8VF+l-9Yak9`*l%=tn(Z7hAOv@yzv$s@VNoG=(vV3^&sn3-8;LBOgu~@!h$eGBNv9ny*Et$2f#kD-Ve;N@e"
    "$}@8u#5tg68(~Ei-0fJr8#OC^&(CJ3AZONW=c<Q`>+P)bn$s`-->b7xm6s-x>!h<q%+W7$|2A8dok`&rqYliDwjW`aTAEt59~^#c"
    "`))jYZ0Jx$)L=6^aXwOCS%EVrboW(;K)i!BKj;2^Q>hkfkvxG$+q(5RD~tR+!s}ymQM>nAGkJ{W^d6hG=3fw7mviaPmmgDDe|jEm"
    "`|FYVT-Wn{-iOBbtd|7O2iU)6&SRo}wt4+(XzoYoSXHe+&%AJzO1q3>*SxUeOR_)mZS#CI#(uP+J@YYA%kgycEjC5JWS4pC`)rCj"
    "9KRX`EzLiCkf(|xzBB(-^SxeHlK%WA-GKMm0E#W1CilR=O}hp9VB7I{xoKN6a(U_`R&iSyZ2N!rbypSw7VAlff)p0KGx^6|EUXrk"
    "^#+uyf}L#3oK5OP{uJ51u&Q$j`1N+7ZF@i2C5Y2@<!s>~sZ?-b2QR+7H;>Vdk;?Da67lav;&#(azYFn2_5C6=$sEc>D`KV#A0gqz"
    "_)hUhwFNSZcc*M4mQ$weo=y7@{=B8K*pxdQY!X3h*Z1lav!>(W;!Mz^;Iv;Ji$8-ZgfLD67cXyTnY0AU+npRl{dLUDSz>-bZ>Y?L"
    "v1A$45O>oM#ooz7Wx-vUVCj}5HT${f?WJ0?m%25tS(h3`NJx*8MeXM&7X7+t)s}Yrj^i;bcbBec`tGMc`RPFRl+y8bo&GXA$)!{V"
    "CY6JZZm@E&V7Y^8D9Q&fxw>V+hF?axmBP!x?k)WzFXtVsayJ%jSWz4beR#QonK738Uwj)-_)O$*p!{5=pT}=`z{V(8>eBctt<jz}"
    "54yL*uU|<L57ki|RaUi=3!|I9s^p@k(wgslRbMigdPXw&HANBgX+JCV*T`#Z&O;Y=j?F^&%G?CPU)yIpN-F}I9KSG^h@}z_ef{hD"
    "en&UJ$%)pQ<geyN^NOI<CdqrFpDXIcnbd8zY%69IY4cs#lq)!Sq*Nb^6ILSlJktFVTUT<)L$R*qov*anEp?fWnXkM_7`Q{{kma=d"
    "k$1k}LHf!G$?wmfz6m&^wIBI1;vKIt_h)Urm+xE^^{|aS{<i2W$E10zvgPLN@|t$p*~w%zWkrKmC%4f#Z1P4##^W;Q)*jmMuf#u`"
    "KPcGwh2(m!4ofrsY|PVh{*g_-{`Eun>TrNwg!F?17nXzmqaD5q7f$Nm=GubFYuaV9<P?oKYo>F<!%J`DUG9uip}%6RUdv~8P^$S?"
    "=#so`I<O{5?9#lD&i6b*aBVo~qjtbci?z#6wXr)^pIp8VgtzMRX|EFnYx~saQ?JYAe;_kxBwjZ)cYDG8f@|F)W@MrVFVXcTC*Mr?"
    "Pr~&O?k{|i7dWn!j)|?G2j02%1cqpCcB#5{Kb`!ZlRm%x!=?}2?$mPq;!erqQY`%q&R^^8<{AwfN)2dNj1hm`)RK%JnG>wL1(<SG"
    "eBg}S2*@)iY?x5o$kW$+DDe@`?FP}J0#=%`TdunbKH+kQ+t|y-civZRZvQfux;pk}H}Uz0sO2RZ-0}b2eLhsrvMFvJ@Bl@y!`+Zx"
    "`g$1lg1hJWEdqr{^6uihvOXo&E1O|LD~$#}GB=+xKEAc|UVgKmou;BRW5WH@$|=TZ^Ze%2taWzwld&x#cYosMlg!P_MrmnT(Zwxc"
    "<3oZ5iZTz`u}2H{D4u(`^OfDG#;Mx!su14hoy71+*kVuokzleVPJ@$$E1IyC7cyS^ft%Um=~%UW>sHX#o@{Pg{D)jm+|P!=ShqO0"
    "t`1vF)=_VIN(c(3j1=r_t0?@Yy0$pCtz&u|R?4XE8Tp;?8$Tzt=biep!loDNo;4R4<@bI%dscl89UEW~+4gbT&3^M)+4I|&@O_2&"
    "Z=MU!i`+`YhrDPz$jVLflf4M-3v05M?L9B?WGk?v61>!IN|siy+U<mjet+AmBIA|OqSY&F+v!!htsv?4-PEgbe-FE6KzwI1czLW5"
    "(|@P3AUwL?;==21ceAhE{n%Zq_rBgJHhA7#V-_jjm4ADyZYN(Y5D|Lo-Ty$)Kq9<rju~YrJYBY{ogo-~u^zNre=6y*`yg+(<H>_b"
    "VsRSpcT<<i_kPKEKfD$|%A)1ueeml`m=&GlH>THYSGGklK7u@(q@-Oq-}t2m-)Fi}`{=08`##Hm@XhVJa7c$A*|#)x8ZpNA2|mGS"
    "eREG%dwh~z1mi~!ulW=`PjksA;QqD}XRtGOpzm``75HPKIL_zT@kdtX3jZEQR@rW2>xwVgSNH9u>|<YZsY|TcSa)Bala^c_vuk@P"
    "ICO))375WEa_4>b+x>mteoXTxI)AzM?r`@AOTE;0FFavHaPi!CSC_+EUGdRAUG?--dn&&l4XF`T=AUgpYH_O@YBCr5^5@*I-t>(4"
    "xnY*GkjU`*B`*^z7(X`h3;9O=s*!u#FL9lML+`9`|DD<6RW(+E{da!cx*ESb_V?RdsEG|D_E$<qKB60mA5h3~J$}6#b3om7W$|R0"
    "^*~j2?Tv9r#DS|=rX%O3@c~ouyT$zY1pf@~c;UK==l(STKdjwmuMYZ+9E&jm#t&ZET6|}U);~Dg^d&g&d2)zK{gOBNH`gH@35i0Y"
    "QnmlF+@q8ex5fZR|AfVA$$N)(*D5DC!pROTZuu8e5ndfW#Gh0RENcshyT1E<`l;9907bh@!(WucnI(Jag1v&nr3ZOKDh0Af1V`>9"
    "-&0MF7_;W`8ikXOWC=Ca28zv(L>)e~%Qlw;+TYhoW}>Y;iq6Wg|8ry&7>)VoQO20~QG<FYk*>1-QHnHK?9EN)qt<PbXx=8jz(ps!"
    "Mm`_nqwRq++!clWWAgHKMlO}XV?|#rwBIci$BONxQm>s8f_%hMRr5o%gQBIM<W#G9A3OLQ*8EfHIWF)G_Q%E5KYq$KDwSFFJg9NT"
    "MM(DN^W(;R?Grr7#$fE{4eu7RERL5P+0if_Mg?P=$g({MaSGPAYgvlapF6P-`q9dD85wL&hBNo(h51Rz^+!L{J+*@ys`Yg;e4~S3"
    "SM`dOs*#<1bXosfevoytmg=~j&f9lNu+4kBit+j>=G1Xb(_Pt9*~7DfhdSA(dPhIc{jGLFbPDB!tlWN{hB6oIimk|<`n~Nn@1gTP"
    "E$pL^{>oW!`r5S+eXeHqblGTr)$&8v>Dcu^okQxvP>gr{ZVIuCp~PNSu@w}Gp{RKsXZFj+p(^*y!_l3cLXC$%M=b8ke~*k>$~DcI"
    "4owh_kch4e{$6$1Zu0K+VW=%_{z>9$Lg<GSY`*5yq|imhrqK26qVK&2&sIK-Ieq^VS!%s-^Wuz`I3nAz+9k}eEthgvBKyql&1-h;"
    "^N(ktf7NWRJ@z<DT5K6;iDU@-KkR*XJXc@*zsv>=BZZ0vLM1zK4xwa3R%GwJ_m)vcA(cdhLQ+{th?9^_R@zgEsO(L@zW4R{{`33y"
    "_wUa?PtVsl_rA})=bYEQkMnxnqTzH$vGJa%%0msm4m?Qosb0S+@aMB|pD(lei9<XIJ{4EH^hdrYPjB`-6s_Sb?JJ;Mr`L93z*jw!"
    "?Ob~I@U(G6d#>7L<QuYKXWQqCpQg`dNZh>W`oi}jad8iw`r%ue%=2B_Ct$iFiKXOv>csT#9|{HQ?lDeJ(R$X~PqxjloR;zUb6m`C"
    "=dqosecwI(j?;H@vURY`=%)>CwJt87v6epI@X>z5jKA#mEm3Pe`(3hXzu!@Mc807DRh{gWnQ1<sX2jEeXJ+t_;FB>c<C)o6mcOZC"
    "F|#bc4YrQ;z4BWMSUJwxQS84vasA`NY}aR%40qdgUDBT2H*`)u^2ApEpz;#CHBwUkSKhaay}7{Uf7RMO|7>)Mf5)1mMXMf{_?Nsp"
    "J9Acer~l;l(L<H=DFMu9#Rs-Cu>^<+aK;rSm;}h|OElenT_Hg6=keW&N7(~(w<UJ{x~3Q4yZxuWQiT89#r6|D>Tx0g4+JgN_X;b_"
    "**tS?@|_3>ct7&)%Sg!J-1voq!uyL21LiVr?|J$mdG3qlhs2!qU4gPA<8SWlOA6fh^`pK|>Bc~}wew8ROSR`MZgZxsXxq#uS!6S1"
    "MY#rEZLs95wyB-ZE!TaRw`F%=Q|zCL$Cjdj%Z(~SM~ht+nC@GIUMbRCU>&)~=h3iZfxrFr`lrWO7gT@xom<Vo7G$GOTS8ds7To*>"
    "Y%a&i1*N3TxB9v(2VD;`IE;%f2Q_<zJ3H=H3+mq__pRvV>_X?7eS5~ZnHL_G&nnq^>jll)vd(!itpwwfYG1z2iUuEV7c1XJ{~-8u"
    "tV-E|g_&T_C(^#>_USHOd-Iih%4c=(^{Zvodq(pXn{P<zW~X=scWckLWmJ|f_E{Y3co6$Bc(T|jD^>Ys2=}tUY-@dF2xoOeNETCj"
    "h}yZ4hP&VRLc~6oioY1I4cT9v_t`GkBIF{^MeaQ-oFTrZYj@~;tXO*b(~w6zEGwkj?JF6-;TAH$X6xSNRvXHE7V~~!ieFw+bN9}Y"
    "Gvl)OA&wIP?iI@#M<&=xzeR@H`G4nRv8P>jo!?`?`%HP+Z$1A&<#@w#B9rc(241ISlJw46=9t3rbLMe{TUc#*;8iz$$27+Z;}aHn"
    "*$3_`%<GO{IoV>evi<U;@@3`M%ZtczSlX<1MUQKjt(Zu`|KDHz|AzltPX>?CQ+u@W*lJqf%=ExFt_IG|415bKaGou|d3k~F76dLR"
    "26bvg<fyteW1_0SCG>#HSb?3KC-^BufL!?^*s0zIxyB=~({2H|-baudPJ+GZTF_hW1ikHH&^zh_y1Ij%X9C#y<^u*c0)~DEjAQ^j"
    "%MTc@3YZA>dB#$bpq<n*!1Q;}ekLs(_qGt&-O&a8y)cj$-39r>ez32g170l#yw(zULkie8H-Nl-2ISpBAb)8N_~r`eKePjWr3W08"
    "2mI*|_`4MBCw@aav%+v*i%y{b3+FXXH%!ULR|`}2<IGgP5+2`J0($ltkZ+X(`L-xPzE<$#X9E;61>AoZ^kUQCCw&CkIh+i7{2AoR"
    "qQF%nfor@3zmtL>*AE3hqh3HW=-+XxNI<)HVCO6ae(rGJjC=nAd4M|bkOI)3Sp)JIC-9GJ2YuoJz?4fMPn`q140G_yYy^GIevs#<"
    "f!zZ-(3iLaKKk!`s*VGaN|4v@1^=dW@M~uQc~=DRzW@5^jWftUd<Fb^8gQ@|^dp*J|EC$+pHcz&Ts_z=Q*|ov#HweM-2@}_`^4G?"
    "kZ(|>>?YXYcTa3N338s-V8>?x@;$?VLf(M;S3oZw5B4%!KrWXDTu}=2DoucDMt~<q0d-+qPZ(|nKa&S=9+t`=xBUQiPX2)ItRVL;"
    "0=obWkcW(b|Ct1kpA`X&?*w_0C)i!y4Dz%mz;9TA{?=N+yoZ4IOhI3~2JFjVo|&k$20dW~tg8cT@&<i7KiGG@f%ANs2=ceefFBn@"
    "K2QdBL#`nIB?#?|e*^hUHsB(R>q#0a&k|44Q~9iTa!oeK*V_QH!Mr-j3HSFTPZ@B&5YY3({V*xK0r0?Eu#>n0{18?598V%;KqYpN"
    "AA|XCQlkRoClkQWzyi=%8srx1!OrFfaK~qWZr1_51E9SCs9QD}DgpM9{~hP-H1LF1pih1R@+(<@>1P2mp}!_`44~b+7<eI!|H+4&"
    "!M_6Ly~*kc;LpB-z7gh&$+kw&cU1y^SqSaF%>n$B0e;^u10PNV``>YZlQAHliv+u6D*q2p(f)@_AfI9eyQxj!H?<ksnc{|ar+DEw"
    "Q+sm2PpA;^Ko!_Yz&bQ_s1NMX0H6}AZ&Sw^fS-VIH>E2A_J%Otr%VljTX_K5$AR1he&-Z?2LMm`eE=T32zF<<L4FqI^{E6i&?lb("
    "|0{W5m);JTIR$pPJirT%0v36Kec4U$uY`4JiYx*)2!maVDd;<s0ec%j{(1rIJ{|-da0DE>1?~QV`C)2uE8yHI&@WTp9l+DHF9BC`"
    "QteK&7y)O!0mupcIlXN!@SSkJ(*jf-M?Ad`*8OR*lYr7UK`-|U{Eo;29)oc{t?>o?bR@v;R6KB#&%mu@z|Q_6aF<c=_k#Fm+CLZc"
    "p>Y3BN7?|Mdk*>w0^pYd<8b=wIOuPj0)Fc$U_PuX(+@6#{vpI~(-km&rfc4VzFq^cxd!|?VcnhX%?0~6Twwq4BH%YzC#Q#_fd7X1"
    "e|jny?B`*9oc>GIg~2oQR6Z)6SsMhnfyxKRGaRr^&v35><V^;9{w<&vhWKvg;C|3c!F)X<rv`FGm|tg(!MZr3u?%`0IL{eFe$boN"
    "0Jqi$bfEJ2@r)Z>ml+?3=Vk&MKpqbB`%DZS_{Zl0CLag+mEYi(0poWj`!MM9z5(7(0(mLKnKO@vfY)3FUVjX*8Tx6a^Bx?(&jRFc"
    "IY9oY1NiqC;3F7tY!TX<sQ_G}@{;i^Ev&P%OtZjQs(`bF0pCj1%f+)h)&cJB1-TH6gIQ4+SF=(OFU`u)gPmd@@MCa4%xe0By{<Z-"
    "5g*u@!F8Us=>oYE)T5mBfO&h?&l>zg6u~a?KfhR7;1|9FztjT!8m#ZLnW-Sp{qJ|&`|mtU^uX>h%yY9fqF`6g3)r#=<S*y}`{qIZ"
    "7Owy7=RuGUegYhQ3-XD6z&ThaW>=_st$2>Umpbm;T8KmEHbPu9w;AT2Ii3Nkow=POfPxUW%^jctlw=0^VJ<*LSg+=e9R}1q0qyEq"
    "0UAL+&zUCz+TH;>=V!n@VZNU8UjTX7R^ZWxfX5pHCPTl?rQQa--U{vCngG1Z4R%FGLH`Kiy16G1U(7x02D@f>j+yI}1m5Qees42D"
    "{<$Cge{2B!r3Ugzxc+nV@Z2&_Lr3v>Mu;=!nL$6#+6uT8{O5NV0Pdmk*73aXFrb(u*vY{9I*+<RuCf!_Q}+S=$tKVnZUecQ51<Xi"
    "xAV^YfS!>c_x}VKCJ%nmuwKn4!1bHIXbtkK5MR&VJOIbdNdv!ot3X}?^XvTMw}1rZjroR3(6_;J)_gbg+x%;Gu=|(*{5#A$^CO{v"
    "<MW`OgK<8;Le(+E3k+0U8oaO$#@zxd#CZ!_;XD?0!~*hf0=)>t84KdDek>e<cy>Vn;_QW^FM(@P^=I&c?h>?jIt94pUeMdufxR2V"
    "#|u95z=NS579ypA$G!oc6atva3-aqt(C%$_zyg@>7m8v2U3lyXNZ@_JLPHnuHh2zP=z;lZ;q?d{|I;nNL1WPWg86e{vKw$AiPA5w"
    "qQ19)7gtktuJGb|7|)9wR6RDl$YTb4*B;<||A3!p6>#ZufXD#kDgt1y4)e;Q4$Rk!MsPlh7EsT3(Ow78Z6C;e*MeQ}5MU(Sr;Bm$"
    "yuFxw9{5#=Ll$pB{I-~@0Q|l%_&wwVtb+G1i?tAcEjE1z?0gOQ65_MP_i)`72mbp#KjA&a;&?Hf|J(zx`%BfK!b^-)9X-6nLe-PP"
    "OYCL9xvKzo)`5I4RsRVuiM|3Z4bLx2XcF)!yw6zDgy*g$Jt072sAIfj1#!!gBV6|-kMm&f5B;$e)(rBPA+Wmu>(|m{crIVc&<DH~"
    "3hmv6xOAx)uK&{GzaW3Q4|t;)=sPZgybt24rFRhbE)9qS|LF?)ad;oJG)L9r!^<>O-BY~GWCyrDALJYm4=!&L2fjNPP#B&wmc?N`"
    "T9!4Z+FMqH^=<h$%rDE@x*$IV$6Gf03vxR{uyZX1x$k;tCj`!KISTH(<pg;Du$+<tcGu>>Kl{Jq<-@$STr2_hkKy@p`6<k|%Z>29"
    "VYvgY+wx0$;O{?x{u?~EEsu18eiGLI<po%;S7>3LTUi6|eO5NXdbY9!-cPLXo(4OC0l))pfKm|8tRRTTR*pivxuOa00ao-CL2vR3"
    "<TmiWZp8)S&=qfp&sKt!03-ivKRyQhQ{a8k$~AZou#)Wy`nx+oUkvNcN`*gQEvySGO|Jl7!~?#<fFEbTZxEi-R(?Bzd<N!?m1U|f"
    "BL2%j)#bx~S?qyxz;n)Do^g=xhUdG#BGG^n+F&QQ9Z=~vpn5H!F2tLEjp6;=Uu%ea{yK95dd))nK`+5B62|x6_*9Um1c6_=ImmAv"
    "1G@r<_y3l{bKBo4n4kVWgLUU`%Lwr9kHFtR-1zrP8~6{y`=h_(|DESN6>tCh|05th^<5nWn$^^Ekpc}f6(=dsZ2SRw_EFGp83#Gf"
    "9LV`-K)z=U`0Zr{{l0C02ls-Vq!id4QU*JD9ndRU0jhX|-SHSe%`~t-c^^>!8KBWC@HhPpXvGL<w*%1W5ZJlt0eX1=`dxr_gYE%_"
    "wZd^DN5JnKGuS2U2Yu2>&|mTc`PB@NXVigx<}mOaR^a)Ef#0_SUVIV!%Lw>ajDoy|3*^t#!2WqKV9Nur>-Y@V!w%Sg9Pn*8*nKPq"
    "{Q4W(`5_4Hj#z=+AE^IMGx-+y94GK4s!p%MDjMo}TVWM_Kh@5vHCsT=Le-yEShXn=kOQv&Dz3eN+dV<Pvl38%7W{-Ypq&G0AQ%4z"
    "av3q;auJ|c=mNP4FSK{u3sCbp=ykRN8n}V{bOWF{542<L1OE0MAa@Z2?hyst=QH>RB9MpP06en{{%6gA$JYWT?E?Et=fMB!FOXl?"
    "1)lW;^tro1em4=?c`y%HY71E21NtWlVE?oT{2O>d-VFD_st$V4cL#v{<$uR}YYq7EE$9beT&()h4(*Q~1wK{>cGDQ-^EH4g)O#NV"
    "TH0zrCh9$h0_{5LduR%@8<jxLPQ@<@v|BYnzO4^%rwJhccR*neus^T}?MOiX&>n*C3((5v03MM5JPOy3R{a#%X^nuNUN~^0|NKm0"
    "9Mf7U1KNE6xwAjmd9Z=p2l|gT@W1m69R-X$4|r}L=o7l&Jd<JGpuGb3G3_-1@|(86Z?gd2DF?s%mcUDxfj_DQtg;7u$_f7UO<>m?"
    "0P+rDI8OH`!2ZjC@6<pK-?dPn{Z<8h*a!5#4**V#0M6!veu-Ld6zEn_@u>nG!w}%w0>BNfpl7G*`YF(Dq1Furx@|C@(Cs`6D4+#$"
    "5ial(h3iNsSqget7=Lv5KRab!uv3M3oKCX=<T`19r(8j90@sPo62>2$?G(tJUI2G50KLyykO$g;f0z<r6pSyrSO%~^{{!qUwt+mg"
    "7%(Fh<XK_RUamdZ7n}qvk^^~}AlOxI22L0N>!tyl20`Ec26%S|`1ixOp?g;W$NO9i^6zjR=ziV;{BslRrqY4W|JNTY)OXVq=;^5E"
    "4+Z+wR2@hKdKT(^xdJ_F79eLX$a(Gq=X(hD{MCTMO&}NT0WJym5xwj$Kn(K~y$TC(wH<(3Vt{(bKyPFM{$}2Q*5^U)kPCLMFu&1z"
    "y$9|;4|bt2KIkK50M8kL{(K1dU(5u%RG4?^Ghkh$&xZA!KJPH#JzK!yi_p#^xF6}OAU>e4<%V|QyD19vt#DoGUzC8nZxGsj3-=ZM"
    "Ctc8gOMrHVVLqY%LjyP^4|elGpkIOU%0RaO-%VKq=f$v|s<*4az*Z0Pt*e1=hx?vk7hFFE!7tSD81{>RojA<L3^LC_kJtf~;5#e~"
    "s<7TNoLB>Px~9MlAA-Nx8nCmr0`36o27?>irwra+zyn~uVhB3`7?lJVI|lxVx?p$dG4N~KfZvP;ygdr?yReQk6hb`2PzLiMLnXu~"
    "|9wa1fB)pa8x%aL_UuF)hBV5@r<sr#oyD2EopDIz^t~s;DjZ1f-J9%Hv3AIcv5s+wyA8Qyzhib(bV9xs^eV;m{3y(G+rtB|wh_O>"
    "@|lBYb`y){;U&6<kC26n!Y@T`K@|M*a5Ifz7;!rPFjJzT0XeC9$-SL+AwC6sjYE1t$a%;1rUKPqV*gGjs4FW4h3_~~^Y!9W<oZXM"
    "rNUSlo%m+*jv=0b;I)^`ZWpHzMPEh@hQ(5(&U<#~j_^L@wyA4>sa!t^TS>IoAnQwv>R#q<Ji>+org)?O)I217Exm8vZ0{vr<q|F@"
    "UVkK^ilq$Yi>pca@7HYhJCsOJaNg55dD+BKgWI05{Rpzo7x<W7bC3A7ZFF~8EJ2>6iT~ksU8I@m_)^fzgX|Ho3awcC80p?&>Sy2-"
    "MLtCi#X;H6h$lzM;E5n!<o$v3<-R>v&<Wiym(oJri0HldQ~j;qk--_pbq!DFP{4Yt%Q73E5UYi{p`f=GB&?REut%U41;k}0-?dXk"
    "A-4*i3U=)wUI%Y|alCj1Ib<<KuRm%;%=B0)lypxMXW2{U+DtOUfI~jvw$vi>m<e8BJeN$Y+s|8`J@SC~z8Xk=oX<qO($l`B#`elj"
    "yD_~urS_AAMh#~Pv(h4;4+d)3OdI)!O8g2n<|4iplIOSBT|lm^5xn$y|N8ZJ1jEWJR%9KOARHTFM#AhO+YRWhAiI?2;-oZbWO8aS"
    "_(MA@@>ObY_)zqfSa;LrUb_@d{De@tr;;jh3)H%o+2D@s)b{sX<5VZcG%lUVw~rE?8@r@z`je4oSt>C|wIk|>w`#uBE+U%6W|fiO"
    "6Okv&>k@mVM?}{so5jYKhv@m%YTB@|Bag6y^19dJiRKt*<-lMuk!i|2x)g93`5SsT9@y=VOx`p;I}l=yT>f3dW6W~Id)?Nw?L8AD"
    "<mNydea0Q)qP#ojt=2LMD6y~XVcd=a`0|@huox2e&B%8DYf}=ozOYd9kQMRXS$e7P!bjv8eyH6_JOg=bJ6~<tu!Z=qI{3!r)>{<f"
    "c=ej2bO`Y^b}rlWo*Q}3oY^UgDp5e5NXdP&o0x3gIm~=<h1e#XmY&n<Le55Kv#Vv7k#ghM&4d@Lk&jAi@Jc`=I@Zs!JN40R<hsH$"
    "5hT2wm|kt+2sRaypWIK|dE_)N2|BS+N==D@_#NR&HTiG=IV{^9bGow;xdd!iElIvbJnB$@{2DFdAz_?-ao=O)vF~<Cy6YhFxL0%T"
    "dG!|JGO)BSgO?D;#<$W^OiRc&Gbbgl+!_U%hw{X6N)XA4vaMzkcF5q}EAbzPPZLkxsH2!WlNi`$W}CiZCjQQx79kIvh>>{kzT1B4"
    "#B+Ln^D7%6bSkcanWsG-$>=4oy3fu|!Ww*SS$-Okppt6Q2Pf!}3(MY`OS%;(_(8G0eBJ_b-CE8~zpIu6vR-Os&oU-KKg8~F2MZ#r"
    ";;D>v+;9K&-zpnnQ*Wd<%EEj^@hl4U6kGWbTZclv8gTn&(xDS|yUzr7=OC}^L+$-ZiO6ayJmf%15Aj#Iv#;;&5OFKfV_>hdBVj(5"
    "75cAnlaq464!XtOWEWxZG!f4y-kUS#>vXG-j*6GI@5vYFbc*o6`-9cQarYZt`S2-Z=VmyO#s3Srq~V$~SrJ54rBtqc%WmW!l{S7V"
    "D-?yvZ4j#wjYFQ!wL_8jy@;!_zW2C{9+4Hu&>6RUPD}+t1{j1YNVvx0&1b9^iB)Yy$E?&e(fcyivWCWic*WJ#l#1~o*WWYBYuScS"
    "c<N$|iB>8K&r0$ueo}(mY9)WK3aTU?ADx!<3s}kCPb{*9KP(7s1^-1_FHzzutRfTSUyFQ19@ZUpEhPRaoD3pww-V2oYY&z_ERsOW"
    "Q?D31jF6`QqBW2ENjx(p1Kw)b5UKDcbv?R6NTDP7iV96LF_x6dU*^>y!ClOU{LFtNwaMnYW53gp|2jj-eJ7YvcvO|;d3tjc%Km=m"
    "F|!He!OWulI&qws?m3*0b_XMWE5yoEwU2n;e)etUk}R>{wi>e(;vxpp;pKG|O~n2ItE`0ZWfFAlrBl-7yU1l!BSdLvgm@TUy?EnU"
    "JF-e<^fqQPMZtMIvc9(o2^eE@Sd1|zJ|bv7D<PHm)-nq9-Z@V~O{O^<N?MVxdT@s<cO_EB@(R1h^oXw!ZSkAv^~m}6O57B`AMuv1"
    "R@`8|3z=s1++DdCfx`H;N;ia+5m%FkA$#p)k@%I@y*qwIBNrpnJs0&4p@5*lohNuyN%;AU?PDfOBrx5ggyvfs@iqG@q2C-$yyBy5"
    "+82)!kB-ai<yv=$dvTUl@klXod-RlN*js_Pt-T*{iS`L`-QeIZz%@slceTFe9@|Ci??h#M8OkJ<3tVSDW~?DP(;rP*uN*?+<<hcg"
    "Q|ZVmcrIM--+bwv{z+3I>IVro)v1x<yiVL6wr;E1T!6HS;+s5soKVmJOVQ<V8)6eBFKyr;fP7w0?9pOwBBo<$uGf9jN!Xvtou%`1"
    "$o1yzL3w3+q>$==)%oUnqI*&+B<1f~VsP@&e&1gSh<2U!taOnFa@4GiAHw%Yc$IFNSKlV0Q{FjUsxgehw&$KBtm?>e-ljQxseznW"
    "H`(4$x1E>^2>8;EE|H^JwNkOG{~~+dvt=qDL`aB3d7tj5v&g{jaMkU^G~&Wu7a&;eM*LZZ60e8V5??Oew93L*V(#rQvT=?Nc`RF)"
    "$9?<vJ3MXtgP0vjpvbzX2|oTLIPM}>{((=#V};c#<aQo1=I@OSh^i#sAHQUds(nP^#%ZR<f8QYC;zkpKha`xbhr+Mufn4OSIFKp#"
    "E{z<yy(X4l<v!8fwAM^ztQT3TdHw8DW+8#~qvC5tIFOH?mFgc8HspOot4;l#GYQEZsLqYZN4m9M?K^3o6SEs^2kb-*h(fh0YixlH"
    "@}2zVxZd6a?VY~)>$0&Z5u06`e1ZJC@72v6_6a8wo0pS;dE3&6$8u=ha;p?kt!Pd=Q9XmgZ<rqZoY{%|eRoL*<zFMgvfj~}Y4XTC"
    "nMr$<+I=Ku!72Q%aSC~S**+RlxtUn*osW^%Q6RP*{MJmj-yxf5vl)#f9%31n+N<<$J=PQv3~Ly7L4h-y-wwq#AP*Zc(N2#@6u!u8"
    "w67x@S@BI}bk-a~_H!MI>He#U-{}6ZnTR10u5$nfmP-=Hn$Mai>o5sFT+IC5dXV^SO5=3#Zbq)7vDX6b8Xym`A0A1hjd;<gUVS*Q"
    "k@y=i{b7|*MttdC%M@3%iS?`kN1SN}vTCK@plRJpbO)y=yhjs}U3ehFgrX2JFb?kD`=kn4mbq<h(&i#oLdSVr1d@?%JH1op%>m-*"
    "bn^g*t|vO8ePRtqx)yPE4SU&AbQNhb(D9@9L&U0Z#Jj)72ibf5>>cG?jgFfKZa6zZP^e-0_gmi*P*9qfp{Bq=qBH)p@yur@!p4_?"
    "l7o1OKbh=NQ<WvQzE+}Vl<7&p;FbM5kHiy{y20A+`7+VZTcT-Qu0SE<)gh<1Gn1fDm(v#Yv&iR`IRjsm5b@O)^D3yjPXg8&TQn~2"
    "K#r9WJHAP}qQENF{Z6}XAlDbiF1}CqA>Ink9in>}i9=I|^JI$y2@#Bl+Ar%(6mOP9kI!8|^2fJxUeORG?v5UuT|tY;n&bP&BbVxs"
    "^ZTq$w*3V}G3@jx9s6q(m=K@E^@fLpMc*5kURjNN7w%rE-%~*>r4sb6WNITr-Ggl-kwHl5;9zs0MnCaZk0=dU$wvAvf&D$cmyn~g"
    "f91wQFVJzC@MkQ{pNaokjxKY-K_b;YKEdY{flg}0q-7Qe5&fd4Nxw{PkuYt}YwOp2B&WtTxy=eMAuZFgy7?F%!qQME)xLg=cyT1y"
    "OXU_JSD%}YNLwBWbyr$lDzb_AN&4!oey&J@4_mXXE835|-~Dm2k_aT0yI=NZlsX~z2Ohf9zPTvWCtaj9P>6&ZyD-r+#iGClj=FWu"
    "oXE=Zgv2}Lf9qAnR>rFV2symqJo9!-6A5R%UVXviHSubGASH5?ow!t<?8wutBc2|?=alV!k>K2UReUu9d0X;{TXKdFt-(0%tJ`Ez"
    "*v(t=1Gt==d^|jVeMAs>A71dcS}#O`=%3r(KJG#6Z*}*q$vZ{lioM1L%C*tSM`v=burni*ch}ZCx6vTux}TEyMxjWnTZqGdo{LDl"
    "x?aK5t4b_c^uMCDS;X_?$7}_~KoYFw>cIK64h4R8;HK%5N3OCH{_EGyAT{}d{ie2E#GKA^RI)IKc=7N&W|3SV!H#`w_AdKTNV&$l"
    "*zfO=U(SQHqeh#N*Rzf~>DxZY(@llD=;9yby|zASCi))opWAdu-}MOzcNkCm@Iab)J=QQe_+XSA+Wt-Zf#wwQaX9(ZO+A=+*sJ}{"
    "%Hl*G7FTSvoq~vEjg)VwatH~o*D*(R$58+~YYSsz81i1D6|(l)Rpc8c?Raav8HM+iS7v?WCC)pI-}B9~AZJs}L)NdlhzpzWfQY3E"
    "3eR`C&oQ@%`~^0gG|F>A0e!FhZuw=Appl&BqMKKUW=*alqf{gc>-E&w^jHo#9W)D)<7Y>vqcqs#k{fcV`u*~!AP)(BPmYYZxuN5s"
    "JGZ=_=_4)@3<CyoX~fe&ZdyMmix|fI7>zp}j=X>TE`DmJN{*JUjm`^TB-UeQee-^@<lxPSVcz}!o^J%RPhOEUMvB){^ks~)h;m-p"
    "CUoo@va$bntwv*r|9bi8(}4;oXbt)MSUduSem*5{H5o(f)IGU6TUVoS6Wa};nY&SF+s*1KS3Tl3$Ry{g*NXxeGKG(=;X^*@&n_xI"
    "5GH{qRBzdY#v@nrcQ(;VqsVc(f5*`qKS&r;aqgO|kI04lPK%i52=dHUcXJ*pCtg2HJ9@;;NI3t_ExYcx5U;YY;-iTk$g3wk&)qT}"
    "dG_bM7_*)szDG_rW=RyF(BD#?<+b|6=OCYMpsh0UX*6%P>U)d=51-f9NUJAC1vQr<^!bQ&eEQQx0Sn~5C&%<oFh4S6yX_Y`D1rj#"
    ")Yvz^C`9)8jk{j>)T0oZs%iILT4dYuJ!<^i6%;V^+)mqY3o`23!94fC33>m{FQu8?hve36y#IQ`M&zNRbWcm*wEPd*1wGze8sw?Z"
    "5fV0g1L>G}&DRBmpdeY~U+{q-uRFZ7Bd1D<XJz;nAJJyw7503`_-7B~QLFg*?rRAY;F7cLUC4H%O9a(lUbaVmrBbn_>i^;+ITq=Z"
    "@3q9oI#Dh-`ZV!ym=U<UM+yb`2Xpz&DiCi&@1}E`ev&}9F9jU5caWvr>0LiWYLK@~=Y?_3r^r~OqsyhHk%TB1t$NFKmiUHy(r+#H"
    "LcsyfZ{~jgTj$=NC=$8WOO7bzO|#lp5D($|+KS=I$T?4Tq|^Ql3fTTzPnSCkxv6w~zAn9iI64Q#mnL6DdaKOeoZD-Mbn48OpWZ4Y"
    "PF@2aq&JTscjNl&CKWL#xJR#{C$<dvXVzB;ENCK)P2wW=?~bAH?@0;WH%y3EOYeHqZKK3zN5v%*+np#x`^XT(R4x(i->P<cP67Fd"
    "Pw}0S5JVvn^Jce3J5j*Vu>70fjwAEuWUMDokoas8aW>XXK{`bTTTVavg}km@{c`Wi6!P1e_^hWr3%RSQT|IO)gKUmD^fSLPiv;@l"
    "ys{adLprku?hhL#qM+g=<u&&PiNEMRSDAH-#KZ68QM#@w;_>j#Tfski#6R$h$nd{)H8|Hzf7pE$vO1XYtmMTQakat@xAPw(pK=>6"
    "vo%)4Au4Td^H3~uEr^|DkbXu2ubk4E$W$PD$6IdFUKK=+>49scJk3x@AXn0u=f8L?^OV|t*Pp~{%bdQwZ9Gz0x91s`i41ZsQxL!8"
    "nu-Eh@(L}^vXWrkg?=^v&BXPQw6}lyeR9y;TQ2lQDst(&BRW9uL&ArViSI@$Vy__ZTYkrCWbe9>`|vkw66llm8k?O)`ttADE7txX"
    "{^ybF5sBBx!_k#a{frGcGQoGea#aO!8yJ)~Vaz9f7P}u*H`@@u$BN2DY$?Qp;qs6<TOpCZJkg!QzXkc=kgnic=ZRB_7T5T}%_wkX"
    "ID7LvBeG@te(PLJG}7IxanRT(8Clt``}LvX7YdNv^;)2_kU0Cv5q~CC<lmP(Vf5zTb77%^#+;ZQGFfpvRjzgvd94yKf8i}le8;9X"
    "2-h1S_ex#%q3x0A#K_di&1{#^Y4)_b9YUfg;Fw|l<I&f|C`-3aZl;L%a)`#<o$>#-K9A76kYOjg=vH5wyJ|r~V%+!i+IXNq3%?s9"
    "4+shK97s=l%||rQPjka21>);c(fDHZ7UF#`LvSYXEmDlSp<}s8hIm{1{k}V5MZ6~jHG;PVp#zfRo8;L3jW?l4UWKo#iPx}L+L@+J"
    "NUvi{_cuW^Vn=dZUzIfx?fcf}C&k=Qu*$@3`|at-+wr$vA<qN}R{g0F@7aUgk3|(2JKRS;d5(@)g^So<CgEHL#>7*4P&oISE7H}u"
    "C_AdFNUV%=J~FQRjr2az{x-3WAnuG4mzSo~iE-ACgO--nC_G}I)+GPRzvsf6^81gvA~WYmE}2n7WaB3n(;KBqyaQH$2w-d^o{Z^_"
    "_Fi2?UQ7`K=Qma(KcR^2Leu++_LW_0Cb$xjMs&k)hkOO`I;?*5;oY4?Pmy!)Iaxj8;~UQvZeAxplACwtfCmjRkx2a_^wHqo{PVE8"
    ">tPWJY|K3&wmS!@C|vdJbAOFIyTXs`?BGXcgCf7RG<TEWU2C2{RX<Do)GdE6TPY*Is&JN>(trJWRekyEfqvrC825Np-5TV5XIs}X"
    "JVOF|KYosLct}F3e`ZB+L?OEllZMd)-%$7_a!<-z5`{gL_T~7s1KIYS^yk$=BzOW5rug&3_jHL(@1gT3Ttxn$S_DA~V|C6#hqaOS"
    "O#BX9v>W*zG=9$TMI0IJeW@Y%D2fCe*||H!r-+>T!ph&&Z9tBEu&qiJn<I{&M!$dBV}gR3EYsg?@F%uj^t-C8M3JiLst`9NUZkU%"
    "GbR+BMGUetG)?b+Bf<P*+39hzNJne$kCp7tD2PEYxRvfA3DP%G4m-M*_^)hV_olCkg!wy`?bC8bUe%e#>1I7dix(+(FWpCByPx>>"
    "oIOuY-}ByaPcjs_oMN@E^k_w){B|WWTg6D=;d@4rOq|3gcuKdWXNCB1XN)aWJ}3Se1wytzV@X&jleATDKk|PX9dyfZ4B3liWyvVU"
    "6QwiO&;9gGi06mXPw#W`pwRA+=*28Y<RoK}T^p-P)PE{T9*O=JKL_;}#DDrk&g|!_UU<Mj&UIyc*;{^#T(G$*oD;8v5)F2(EpWYq"
    "60+z*pR?~q@s;khnfj3^;p>-#J>Tx2B$FRPDhuKy{_4QcnxCrVOjWO1Evh5-B6msutpeorr?IOejR~FC5*OnMctV0!XSAdU7NOvf"
    "C)@7&ijpXS>c-eSLlhBzhJ|g0i#X@~9C0exM&gtXUQs++jN+a;8)h~&p-A&!d^}JGMSOI<%f61Fn9#Z~m4%NaDPnr2kLEWCu8>-n"
    "@qP>PHCg>?VWN)2Wc6<e;O|9e0tFlnt3N{9{}eOTc0>>_KEK%F{kw^erJ6XGDhDxGIT=@?;Dv&YP4?{xSWV&vb~SDL<AXfXl~d&k"
    "-AKTuC;pG6m&n;$HGFIe3FI82ztHh3hXjinZtiTkikws~)15B&An{@O{CxEbC~T_z<N8<q$ZFX&Vyt%$veQsqeOWLWMauYD86@|U"
    "7?z;2@T?6ef?nhJ^$u60zCQgck6Rtu)~L4C*tHh<cMiAYjcSpE)yz2qk3^8aMeoKBKP=H6RzG1;GhSpQQ~l6&GzCSw*!_|D`0U^M"
    "baZ2k{SrBUt4nKAXD3N?e>1n&GlfJvaoA=oeG3JKyq6JMt3&MOeP8JGT_En|e|wCsr6I@exc6UeGDy5`%kiIgWl+rW!jso*#pv9F"
    "<qLDWl}Pkoi;4p~l2C-~$?ZRKeUMw2{`Iz;3UtQj?^P>vXA()%R{E;509}Y2J{fiF6iIr*Wi@^J6!98aK6YMJh$K0@WmXK}K#3(M"
    "=o?37Nod3LHj~Z`D3*8FB1|L|MbqRT`LwH$#4oSx6-U>RUtgk;*XGU0b<wGi&E`FdixFjixgvrzM4D5Fb_}5dCvRKI3u&X6g`+In"
    "`gM@*(k?pD;>*ZU{h)&EO<Iz8lwr`Is{utXEc!4s_K~C<Q5QFX4rCF}Q}tP?28rb-tL`iB`saUG|FIb#vNEgx%R^s<0`2Ess!h9-"
    "Gfsg&;%^L*m{950I*;xnnd7a0M$hn)kk(5-f-guBeWweS!tWzU!i&`$Z$2}VxTy5HtD_Cb@{eO{|F_LVHDj+)(EvY+E`8n*+&zd~"
    "zj$9h^Q#k`TQ5JqPLCkd4+mbfooYtGNlkVNw?7cyb=p3aAFmVZ)P3roPHskte@K0Cdp1cV;uVE+;{W0%p%FFO+er5nFJaJmLlV~~"
    "oZG?HP7;@d&$;rs)eIf@n5gxOhRDU3(y%OT{MXM3*B1PIP!gSd?CQz}#IIU8>@k#uPQBmn6KNMgVmsv1N>*8t$coCf$6GB>%$ZB?"
    "+`fM&NiQ3$&zQYK!EDc)vP1u(3&RTMYVVYwGZ(id<|>{c=Ohc-Z-w=d^E-t%^L=$hhB*V<>11k=)5jUz<7<^k#Gl)$hL6>VNnNPh"
    "ol<rZF}L!(EnWe+d@OKq%#T5~%=Rz$BoC6a7essa<hc?5Pe*49F4L0u^lPW%BZP>~&bRF;BkV+f%in7fOUWd`b)85zM==Q~Hr<m^"
    "yNkqd#fiJb2_awMu{K_|eJF}9L_FoiMr8T<=dAJ2zxfA+^Q?>1Bj?SH7*-1{qcg)hv-yf6Nz9D|=7d)nBr?DK>=u#TD1nvHMucCA"
    "1Sl5{nDB@Y_fgBAyYdQ2>^>9k^LLz(Nn$9yI1)zwTwj;gZ%sio*|}_Ichiu>Yd+c4WAr3q&n1OB_Ie~*)lqwm={pp2+~v2PwhM{c"
    "eQlKav=0foFw}NpZ!wAOVdRy2^cMN9t3B1h$BQm7N0jC9bE71d;#=JZVo}6P!_A+*$dRCI?wpKeZ)BY%!69oikKFeOFkZ5VB9=}U"
    "s+wGrNRqs_W?>dB@#MS8dQiQqW-Qb>oNZ48u{Av?)IDWLVh>tekHoRa?e+be9)1fb{{AMKm>eCFMEm6{%?~{kKO^=%yh8|iHpl$>"
    "tNocoj}&ws%1T3;GKVh_i6bcJ!|bFFlM4#5Up`F|f{^9Y@Ti0uITF5OVuP^z0~C4YcbWM{E)v81wxyzPg4kER7>=9NK^)9$4L07R"
    "A-cJqeGS_*NYH}8E+<+Vlw_9tN$PnvvMlAhCab|g5*hXj^V4P#x9r=097<h~yRyDx`j6`<;?a#4H)t`6(!D$pSlNfdC%(Up8{CYX"
    "U#%DB*wIZ~Z`-q(=By*}y(K?b85vQ~YPxsXf9{a*Jx$4%w-usr*UiQUl08XuSJC0P!^Ox*g5#D-oGLmuq89Q~)`^@I=eqnmM29$E"
    "agCo_TZkNz%62ilX+~#cq{9+jgi!pQjm4)@o5%$`*qWd&K+cLRc<gZ2AmLf{H?AIiMZC+-&^&(cN6cRy6x_C&5ou3eU}5fkj65Te"
    "GcV^^6d|9q%G8Sy#eQ2AdbsrlIlm~;PJ73YoY`<sdXN<n!()Q7dS>M)sMl0e%Qu1~*{kyhg$xld12Mk>lXWP<eN+3<$QvZ`*pP49"
    "z<Lz6>RtY(kJpG_YhBbM!4#C(uX?M#MFWMbmDAwpEk(NZ2jAxKIS}Ki?GGkxgNTV|lx6sxGNkuv*OSDg02FpT&qIy2k6hR(ZRT}("
    "3(*zmx*A>j7A3v<+&D5ShrHX*<~=E$Am-?%m264_@rt-L^hctM*egp9OCB~vPM_QCY#;TZ^ADbNA%`wv^5;WY_1Q)e_d4OJl=&ix"
    "*Ur)vSZ|EtM1||m6#N@!KMsaJjSnJj@%PM<=FCu>cJ{`E!*$4Ub2i`e#RVd=GmZJoWCXIKzg1Xr)B?r2PPe7rcO$OG_R8;V<ValL"
    "5Py2t9dhALoq+-O2NHGu^Q~8i3EAAWJGC5UN}~2#?fA2rm7G`7JWfJcNlfke0L`y0NV1AE^VI+iiOmr`5?MWj5^uy$g;ocVIGN79"
    "-d{JM&C%XQX(4?i`hBW0=9?q2tK=4Z4lNVU*PZVYa)VK9d6aIvOauxFuxgf?{f46F?U*Y+(2?*UW|#Y3hf$L2TdnC*ZE`_$+V#j^"
    "W@5X^=ffY(EE4N~ASv*X13Bxn_s$#-KT^zUSt#XdCTIM2VA*0}5}c#=_VU$i6i~yM6&#>V^n#VP3NM8qyB`LEVIeCd-u<W5Xi74="
    "a9pMLeAsIe*^p}B9@v9os?)cZo$p2Gb}>8&i|iyJe%pK8OO!}FlX}kkM~TG0KivMzK@)V|{hEe$+7L=IfAhuv$1pM2?#7>HcYt^w"
    "KagC=wFT<!id>`lzy7e+63zeY7pQsedtyv!Q52ic(Ner$@6XnAhF;iymfELQQzrgJ<OzE%b{|_y>3^M=!jEPzWADj$O8<95hF@;+"
    "TkQXv+W%NHCD83+7-WKje^B3{tobwb)s49{0*8O5@@HzM{-pWSHK*b;Bh+^n3GJW**M{YtIO+$L|Atuh+<84mXM|(E%u@RnKG{x0"
    "hFUt{bMLABuV}-WwSFJ=u;I9VYX2mmJ#@tTgo_|fctPz)Cv*u-WvD9#UuagR>J6`9m0{19^TA2A)IOh@6{a~Ei#iRQ{9c99Zz*a&"
    "mz}hPFTSEGClGc^_N}r}%Q&T%+OJJEs^!bG9mv6#I;s3i`Ja-)cLH+-@#U7A)cH*)_&?n0{|aAeI8B}3ri$L!OEr6NDxvltp;fot"
    "vp;Fw$5$(<{7m`31`SR*nO!*TA@x0O!e*c~{x!D}U%O9zcOG%@JZIOW^}y+QUex(*ACkP=Ur~-TGO7JMWQ(?&1HJHdd_9fIqd{v|"
    "B@5geevfZlr1sGhwtMw*+aw0@&3I~mAmN$Zr8^behBG6n@1!H<F*}-T;|n-Tp4z{Hn658Yt1~&^tV%7oo)S|U>H(}cTawzhMb@Xw"
    "NS<?3!r8^t_g@j~vC_XWmo4xu5h~xIX71kCS3j5n@U1)4z8|u0g!BB5pcH(2muf9_Jet$SZbzE&?VHs8L9&`*?HS{R%Q$B%RaXG9"
    "mb!X-X6oUb%lH3BFTdatJMdgM0_SeHM4dm|=MMfgKVReAcw@?+SDIVc`-%t7V_>50w?VH{svE^3a9%i7M}chbkA4xw$cXb6s60@#"
    "tEoJ)I_d$w<6{Kvr5|PTPUXdSep7jWL`aN8i|kUv`40IM-#*7`CCjFP^S@Hpn+QMuX34%%i|?9HbrR6Fi%tCtU0(QZKXw1qjM0ut"
    "Ei{_p0<E7EZ(8S7r_HN?3tGG=|NV)dy`F6t#rKX-`y9!(4xY%M@BR2*HMQ@kX8E=GQ7#o4d|#5Pw}5z4c8Ij6*W&wy-qiW7%Ab8X"
    "zv=*fAVAfvKpf?pb9Obw;s;sBD9+imJ2%OC3>R)?g8TVIt+2PW94@>_?H@#Y+2_np&7H?ZYpH$X^4V5-mLbhFxahz8frq*u=5W!%"
    "Fva;YF40LJvBAZMsD08z;>Oz&&81pg>`U##Cc8VOw`I0C<KhzN?}HP=*Eou=;^JRaeknSv&%d%R<uNYVOXazvjqBn|ScTJYiLEr)"
    "o5bwkype-TvZ%cJe-Glmg{y9Q;ga`Mz66omJ@}+J+ZvZ{p%P9A>)wDyfq@QOs!P?aAfnSF!%Xz4xHKt>YM=eElVpFs3NCG<@)FU8"
    "!m-)Sx-$47Bb7f!g!4wEwpks-4;86=1SG}X-Ia1J8b1uB@_WdxqU#m~8UJ_%m1lrtO3HstOBUdVlhpn|v{9R`A@Ry}T(+P3-f+!y"
    "M)H!f0WU6dq|P7h^DA!;xT%WEa;g2Lgd-6Bt+QmuWuG@ee;$3*mPt<IN8HqRqHF%h&9S~)uYe!vQx#gs;i)2Z2k!v<D7lT|G~wH8"
    "VvdgCM{U%;LnQV~<<G^vmvK2G_1$qI)m$WZf^Rb}SETZ45cmAgT95i8xICEJM@fWthOK^g+#HveQ~Ak6Bujdboqr6Mk5PG%XisbZ"
    "Rp}N9{8*S8?`UJy?a}tXUHGx>Q_5b>NO829&KN(=qP`PML^CXZJv0l!kKg)HTrB#Rc<_^OT)|Gjo(Z>9EUDv)6LZjiLxMtL?^1C^"
    "9F<>z#Iy>97M{@Jih31_OC8MMoxWd&E0*E+NP2%9P3CUHmD1F{Y$R!9_MzT80#|xc`GiO=$@(+0rNx!^j!^n75uFd+A8y2z-+8Iy"
    "Nzb<w^`B0~Rokh3tVo8Dr;pQh0aqE8Q~fV!aP-*LW6HQHh1y3;Hun{HId_%gs&-E5_efWF=sxQ*!A}^<;Qsxsw4xHV9Y4WTo*g>8"
    "b4R!C>yP+J0F~E7B(zw~W~*iKlTt+4i#rVa{AkU?Pe$^o<H@kw+nhVT6Ibt{@>pv=Ki|e=`;`V)n^F0%X#eBHv%>d9arISdKPeI#"
    "@4+9t>2Y-zwV%D_{UX!-l<Hbsvt|~K_wez%%)dWyjS?I5pUXp2GbKM<6S9lqTwWctQYvY<<`K1jSbi=v#XrVr2G{(i_6?%F_uhVc"
    "%2kVr02B3l558pK+RPDvi8+=3Oe9{vTo|6!z$EPv)xSGC1v`h?Vln9sr1(C@F-|j;68!YP`J?22=8sky{PYM_ABD)7_Od<}`;4Ck"
    "Q~4@2lg&HXHgqfCr)BHleE*(cm@$5fpN?LH`%zUW{@!g9T+2%3`yh#T^Jak$mT>L<C$Rp_|2)NTdpE9C8-eo)O<zd1ZO66t9F+Z$"
    "RwFl|Ev>jVN`^YV0>i6*%ezl;Z6;M;0-gA=wI1Crz_m}PyiTH7p>OiqG7Z<hqV|Q7t-%*0+LS$T?PMIq<x_9mHX6EupKVBl^?Pqe"
    "TvA{%ekObY#;3`M@1s$SpB<y}Q4rsawI#P=x8P^iRK7gfRX$%4s4b44g~NQOx|FwZrHmgx%b@my6Rm^$8(7sh;b)Jj@2?}31NK>a"
    "8R_w}UTQxy5t%4^8%JXCv)@$yC6Y6ai7|Z7kL%Xnp}6YC1F33U%D9f7s!M~8uRYxsdU6cc9ii$gAf+npuYc=fah>Teic1E(yd9&p"
    "1=j^q`S|kFj(?Pd#T0Pe6<z9h2O@;MUJPBvb;Z;^V<L0CiuV<hEUs&(^2>+>JGa^R#X?*+M8ywiH4D?tyCb!@p6(T#&$sZNmCIJR"
    "eg~CDMd$||uV<tt<9b=D9te@#G+-%iN{j0asC>Gbk0Z`)&RZjJy(g8QO0>RsBs7RQ;ra{Ie1eW|R$6`eVI!{3r>-|S(rFUEW}`l?"
    "Z=mWvpcAw1Zc4!>xc*ZetQY*=_nkU#;rc~tej#d3uOxX}?Qp|pD!;g9yf~ItMv(?L9DGZiFO7DjVl}q~ZqTIm?Gq)5$S-Lk{J6n^"
    "s;h+dtZP{IS+9p1qNx4Z=uk&f)#dBSxZ&m!#RVJYtM{e};)W_%zhv6<B-I~I;D(pZ)b&1=HcDH&wjVc)rBiyTCpR-D7FO`{b=3JH"
    "S>3bcS6Zd;bAD>SGtn?pZ#L!rr$0jFRTF-WVXv#KA^5o|70)8&UHjZx-For!01@i<9s1RqV|_9JKfgrX@920MZ%nUBHGW=5<+mXT"
    "U)5>Wxi$DXRZi>Qc(rZ))<0;7pMN_H_lNPzueoXQ`1xN^>i47K*M{y}<ZvSwm6t+Jm~Ud+<i&~`C8>Hk<e0u;zSc`#+^9v>nL?uK"
    "bE!+WQgNeG2X#EQD^6!;{_^0)80y3D==kr&DE*ve+?Yk>&mx7{g6^fA$8h75W7PQ{<y?9uWgLkc`!`a*Uv+TbfY-fv-1y&mB>CTZ"
    ")U=Mu`$fmH3w*_b^>7nEwa*>lV?znN<L7ac0+nw=B*T--U9QpNCgWUKFD`y~pPSHtoBT9jen{dII8JvIHziYfHAudp(e97#P26-Z"
    "4%YLt&8nZc4RKTB4(j(RrnT^-zDdSSpQ(HkbX2s?`$g14+_XsbAK}|s^!TT0EpFzhrGC$e>U@s9As2D8r~<5S(l?Dg8-L(twI>iS"
    "O`2XP_@s%OZK?T^9Fv)p6-Ymgo5Qmxz1k<KKklDqaC18KJVlg*w=Az(V}hH@+^OHciJSG!#K!%&x$_0|*Q0&=y7c*Q^ROU{hgesI"
    "0>ez)LPyopA}T)?<zk%H<Cbmhu>Lx5Ry);v#w{|`zH=mEVBj4ioQzv^sC-VOF=bHZrznbBT&_`Efidrvr2T%}a+b>bB${F2QhPL0"
    "a7#87ub`u8F)4TBm~qP!Dd?|A`j7%aAKdcN9M1p7f!h)*ytw5Lm4Ahf_@#^Yu+ieyHB>$Y(cEJ1XYZ|zTX#`;Nl5GKBkQfw8*!^V"
    "l?R5T1(-=!h6HXs^$G63cctRo=@Yoslgb|^qS32kY^4KmYXUXD5pHts&`|w9o=fG?k$uK{6m?wp;nt^AzAsU%{8bioy$H9yf$^^u"
    "=}mHYXmIOf3)~N@!oQbXufuIDRNW}T{wLyC5sx-*6QJ_e{`q%Isi;cfHbts_711cuKN+sqj@yi>dNSxl(xV)=cpBX1%MZV=yJ9I>"
    "!V0$~QuW=)zX#v=_KqRkmj4Xq<L0+wUvK`#ZFOfM-pCo$z0Yie+uk3A^KC2pwP)oEZkwU%0FYgcqk#q$3b=j4W4K-~UN+N+GvoHX"
    "4%GRpoZnJ=d$lTVS7L|z<KE_a-sc&(-Gs{XM#{3^cHar!hui&(;e0h6UOviD$L&c}oe{L($>D7ARR`RDHxaJa0dw_3lj*p<p329Q"
    "Z?dIT7)+zV?eD4la-?Ls-JE9WA#R_c>Np@dwuFj{9gMhRLj|mlkCe=EZCG%}UP;P+oilO?cdo@9M+zxDUF-geRg0@}hY7@!%EiiV"
    "Ic`(9!#4@WPtC&B8dC|}kw}eiq&B(Dbc*RR?#MTV^?Q=*Z~BWI-0`d$)>A#U$V`!+xZ@pFHwvkCUf;Q~`!nvCa)J2k+iA1N;%eN<"
    "QcYc7HmAFfMbTs2`Ct5__+R|fsh|n%wW-$6dYr(WM$jKB`C<Fpls4c_FDf2K3Zb{FE?)cB-gzp|5gjQwZ9crC8F%JNK>zN#&(e}7"
    "i#v%G%>OEDe(p_+#+|R?As%Rr{3w+-fjh?@Q0+@sl)B^`ti><ZP<1Vk0-alz8nX+2u@lw@)viCc?!+_W7l#+1|26IHTXR0)7y4^q"
    "JgNsvGjYDhFWfk&-*@=s_4KPj&G^MRZWupKMO7=0_Tm>=JQU{>V%bo!9DrX`Qgt24k?dzLy$Y)Ei=GXzUh*E}aBWk-FGi@}M`Xmu"
    ">{SO-an~w%A7b>l@@2t+PTaNLg*v{}BL#0RNp0N41@CVTmqhQ>5SPGR0#tvZ&2?gv-G?S{mpGOGhRp9Me2Mv-gS!;=P`^j7tV`kT"
    "*AU#LLFG{rv*0f)&bh3(3+g{2xeY~}*Od0-F56So@nqua_z%yV$6cOO{TyW8VZ^eHb2aV?qw@2R-gvV@r;9l5il_4bh*4C&_FPdH"
    "?n;IAO5ccc&{~xpcipDy01(sj?mSuN|M?eD@hZ}Ejh;k0I=JgeJ9T_xmfh8D;+(jvc^h1xXWBhm%>VtKK3MNhr9W2Z4ZVoFK0k)_"
    "Rn<|ON4E}l{i1>MvklGhJUxxO=HY#nQKREM`z(aJ8L0d$a_DH^y&GpDarY)Fzg@n_%kEpS1`Y1szMkq&9UW`cznd0tw-A-Dk3?eo"
    "O3dXQaJSSs>Ug_vs6@`R8{+OGR2?v)XS;ab{^ljzeS(^QYL>qb2iblq#@)tLyh)e}{bYXe*Wzw_DqoD~=^2eLSxe(?@AGgyujL)u"
    "{I?x<hgZUUBg9%&C1Q%Z6TZRomCgIj;qEfHI}M(1b%ft1rxjP=?i_J=Ub?otc6u@mcNd?c_{p(g)k2$O++7XN4_db`rUgF#cl_ow"
    "xIeCC7F9d^<9*cg88LJ;ttyM@#ND5%Iz(u1#iQ}>x)!*5bQrFmU}5kUEgRfD_m^tlO!d~pg@{Pp!@x#ybMIo~m;giEvuO|X_u0+s"
    "ZtjoAJ=>^yUP$fnzJjZ7RB+GUBh>Lk>$n{KriXBkq$b5rEBTupRt(2Iiuw?LEC@3Fy~criG)*YI_LYrHzMmCvj}cYx32A@wJM?FD"
    "3huFm@vfORnfs(Y8uxfw!tcj1@^YauxF^&c;=SXFDbmN1aZemo{}JhaJbT-$>=N$zFCNEKJboVcWFLp$<0ss*QTX5Qdw?i=6*s%@"
    "Z7I8PPbF0^iAZisaE)`ez&+0)e$%p8lpisf!ad#VsrGb>f<k^oBHZ(yss}){J@ySd7s}$Ep|9|~7n~rUr12j2OtnBfaX>vO@^}^Q"
    "r75KJI`gelLZ*DUm-!;}fB5zqC*M)ryTudMi~OiH(_Ytb?`~~~w+h!^y3p}YFG{`7LI#GmvF08HxL1x5`lnF2P%)7n_a39(f1%T9"
    "p?du)4!BqMA@qme$M)~5F5_NvDvuSJT-u9PyBOkL=Tk6Wo%_(!HFY2N`crkkh^c}=F3UX*+#5Mb{eH7cC5+qndU0<eRS%7*el;SQ"
    "M=fw~`dO-dqp6dL-?vKP-n{?Q(v`>6@P6Tx7G<flAdw`MzR6lrbJB{EqJ7^>J3=H%B2q#ULiVl5u4qJL&DOoQZgsnR+Uy}^`OWV="
    "{+!Ruo%^omJkN8^oYximv%<0K@pR_;sw&zGCx=hz(elt(L%!dpmV_6xrd&^h#;2r?4&^%6E;~naAvCg=lK1;lN}tl69)L!n3idZe"
    "`{mb1OnZ9C_p@|}YFVYm3<?_i(-Dsubn6*iJOiwu1b<Uj<Bk>dnY#mP6sdbb2flg|+o>=HSURNc8x{Cc<wL-r0<fmqA%3iMt=pFs"
    "2&|c;4i@b-sNK6bvL09z!Edy3#^WrVO`*VAyx<?+T&L8t%??;z?~qSO<O0UjHvlUv5A{XS_tBjJ&A>_|`WF>wBp>~>i3_YWw3mK<"
    "*SMoMjRV%!c=Tt+Dib|c-UU{n!vCMQ`6Qb<OJ;%|unw1@{mJeu>hEd<)>#YEKBJOZ4l9~I0qg1u#HU`aic&GtUYgW3p}f|mm9@Ga"
    "1lH3}xSusmtsQ1`0E<oP8c<955C1GW)(0#hsY^_IT7(=6kvj{l-UH<QE-+|%+|w3V{p9;)I$+0xzek@W09%ge-;|-R^nk_4LST=Y"
    "hVy4VVrZGu6kv}-JY#)JaDA#lKd=qW$nQOz)@^&&rVs2H<;W)nkMz&aC<3+(sn1C*Tvx-(mu0ROo<O}XX`j}nh@rst)WQ9hWE<*#"
    "aTTybNPQZLDjeLFH0cSj;|af~ypCrZ>|VDM*lUq*`Z)S0cpkb1?5uZ)cZvhY);(<lc0Q?ZOjFK%778040=tCp4azTeedm8Cp8@+6"
    "+H*IpQ0vFRp}@XO>c-S`6$-{~u9N|GHK`v%S)EIW(pJm|c0I9Q)I6=|AwU0Y0rnf*A4C7t-}vBW3v8Y)@{t$2d@3I*1G_VwjBkid"
    "+)b5IW<0)f5D#g%G(B)03G9FT(T(s&E8r;S;{JVex;kl<E^st?$oIBnY*(o01<s@yq&=PnJrix;`vS+5=;!p}T`BD2lNJES0{NfE"
    "%tKp@?2UnA|IePSOUe9GCj%U}c=G@5Czpr39x)#{ex&{ty{O-M+^<E<`y+{dLHUlo{n+HoEa0S&{X)qp)@$U~WCAB0@%FNYZI&8>"
    "tH9azgghU7SmV+|ySu>It4N;r+Uoaq>ZuvPIpRp#v#e~cX>xKWaL#3s_IsDjQ(V&94V-I4pQ3}F#Xnek+#fhJsk=kl^Byb8#cu)5"
    "GvsH>#EWub10#ULMt^Iy+tA6vBNjLUf-h+=R`B@My>Y<lp~<!1U$v5NrRu=>-i!7(m6zBju!AO9QfG_OF4(`=a-|G3jj%`jvOV#c"
    "iC-Z!jUoG!@~~9f=Vq7&O_R}HyFMFopFOP&n#^vXy)8f5sTAu3P4h^7DcUYK<V*ehSZH$SNBdJN+|%_Y3!2;so}xo^9ghtBCxNB_"
    ";@|0|0V?X8TuW$*CiQ`+W%F8J-k-v}Z)G%TpN;CU6$ksxp=l%Gqm;W&mBuKBzcp>&i{oFEe?Q^)3~1Vmd_9Ecd}5<!3p5=e-&4~*"
    "Qu*2Sj@zK=+#|#j7HrjwIDKfkM!t`yr^#1&9}mrhCYsa<ryP<)Hd|BUpy}y5Y+q)FikIUPXkvXte|>!PUb%@Apo!my{5D-7T&dwJ"
    "G<B2xLC^SR`z3J()BkS+h~F;s6@?XhL$k~P;%_HT+?e5o(5!;^*Fs@$<gP4LXx1Y2x~QNs*8Ur}hC}ltQtyWfK7S?jg1iwln|5G)"
    "YQ(;==6UAOY{A2Lm}t}6De|4rY)9%_QT`M1v=`0Sgl4R_K>5zHR+4#^3eCQ_z874N*>H+I3z{QHeGS_7h3?;e@P+22Jvg7URLX|^"
    "YKG?Z8xda@8H?SI>p}C@XvC|v!=3v+mO%4v#N%G`6btr^bAaYU|L~gpusBX>AT*yQ^;M~$Luqo^Q$9iSWl|T7@{iWu+}YI+&DA8{"
    "M^EBtm^krMp!v}))OW6|&>VHa6PjNap+5b~#NV*07n)m>@c)iZH9fnPx$eODlwaY*^pi$2q51O!w7=Xu-Tt65Xde8Ec*oozi`~xw"
    "uEJwn-{RZlVWs}SRU`2x%Kc!_@_RR)0e5^X`kQK>2WghmfID>#>VH`;t{R?d1MW=Z&%S}>PlMeIfouI7?bpO5*M6ss1g`Tx|2j!)"
    "pxU(^xc~H!z<+uOH;Cv#l#5G|28@ygZj6ZZ&%<oJgg@*ia95o~eRz)Mwga-6z|A1_?y1@13Zz;psld%ee>77X2@TGdfx8#=@qj%~"
    "!-BF(fqP^>>N}g1%B%Ou0QcMyw0}IwTOY4r;9etj1Suc?xf93NOa*QY@||Ud>suN;cLMhb?sr3hy#`O#2)K=;ZUXJqtNv(_Hq##7"
    "Kfc=VGTTC`2i(pyT%U=tVyoT@!2N1~{>nDy`iMoVfcv`v@seifQ|lwD(4w>k?f11uZ{DTnK+9-+zkBiBlZLOKLyK-LSq}jwPH~3^"
    "gQ3MJ0{z>TX=kRK>xGtCr2Z|XH?>jckmq-3u{nu&MdhJQxmh%{EVM=YAibkJ?bkVIS=NSpRe!|S4DXxJ60{ca)D%+-jR_{u5{rDu"
    "?omcRUuPM#tRnk?@{Z?rYn_dSmJCwgiMGEHdSuZNOK92t0)HQL<=_PU574rg)F-BGFQs<psh2}bX)o@dLrRPC7kWU;*$pHf_x`+D"
    "RHB*;v|Lpn&-*%rgnEZAhL*det}(S-E&Iweu!fe$Xpi+DZPyF+?T3~($52nM$`c1~X8y0u0P*&3Z5g&sBD8dzMSH%s*5kU~CusR>"
    "jQC~cC}Um;^ZUW`s4wQdI(d0h8MG=)MSgKvL&w`K30hT8BL3Ny_O0ymb!gR@fP6K*|K{7tFQ9b_sZUGKdda%+OMWi2n&Wu6X%AFw"
    "EO&=it8CP#ei%H^;_QM}haVWvYk07xVW=&%E?t4^uXW1S^e-XM>eqtyZ%bvm)kzI#jU@4VI%we5n<!&%XiY+Y5@h`~=*Xhs(7JvS"
    "@~7dK6KXd7f!1u24?>%Ge99Vrxf5FRzaU=!a5((QdRJ&I@x}Sur#k4j`wFz4Aa#o<|Hu9f_7&aGT7mn={ZZ1P{9V(a^;Q=0`?Py+"
    "9d8Su^**WVL^<jBYi#YahSnDp&d=7iG3H{XKO9nzpY|wTeY-2j7g`0RP7M|4ROL3}q6xHOy?rX^tWNrmZMx9<jnsRi7qKhnN!^+I"
    "f6*TV>8NgXt;&NoWwf7xb`Lk)&n<^G4aB=kSQD?F2@Zg^37?R!=>GQ2{csi9j4@skBpIFFGwLn0&Dw?QSNC;#dRZZ~*)*Yjnz`)i"
    "E>~M<TZnqtlEM8ho-1>qZ5htTa;;bKiY4CA7KriZC5Bf;OU))gTl6>b|A8`vN@I+jp>3rl;xAE>o6J?Fed+5FPuC?~&f-);TMqL1"
    "*{6+ZMbl5v_D}z#i2fG{ZHHzf{|R4g?Xkrl+D;|od^x*}O~0!TZI?*C3~ida!|tn0EwtSx<4-$BDJRJ5GwrF<BJX!R74rMra9?O^"
    "z<e8-qM8onjxuO#%0Pe6b$#_{&2!KuB=r+1XO(xH?*mN#dfLhRgZ1t9e?HHQ=l9|0FV>iFvs+gKPi7wC#gI4G!`QCCQzrFXX^(v2"
    ";g&Ozz|+`;@sOJN-<}V818>50<Zm-p?0xvy1b9X*XkV(<hkjL51>Q_j_nMyg+3vh(bSUs_NIheExy$>+q?KEM=Zx`X#n$R8%k~O@"
    "=MnZVK0Vd5>r*E10+65hi|VtVE13f?sucCBA#%st!-IjBd=u^4dd2SXySjn5{uSaov&k=4-_!wKHp%ay{nxy{fBDiW;N>HJUF^`8"
    "wcqg=@JiIsUXS~EbM{vS;GHl)eEYScpy}FI;FS~omDaV2t9dn+Y0piJPrL3=I<lN42fSKRFO0HZ`_<<UbsKokLQv1=C*9JTFb8-n"
    "QiqV5rKrATu%rlh?W>XRSZQW77kvU=C#eTcFDjn#?C;Dx;C;dUx1>YU_nJ*5@P1+Z(@%kY!#2$g+7)uqe!Txu>v$&_+EsTVUW%;_"
    "kyqXf?c;VJ9-ek)<DoB3&~AWy!GB|d;rN<8&~CPs++SWKQdx7@8rn&jbp}7JF7kM*-4E?{xSst-R;B)((+%yeM1P=t4&)9tn)9ID"
    "o9N-RcTV`*h!7guLxXVt)jl=*kh1~W<J>XdgS#PhoaJk1PbKGP(80!OY2&v9Li?tfh#wvo*DX;sh4x(Bk2XJcR#}_GLi^s4$fpM~"
    "M_g=t0_}&19!vYj992HN#}3+0qdw-cVd7cux6F84Zou`V8D7wQX(hB*;d(S>n}0mGv<%wo4&rz??W)xd`~d9@xIg@2(!Z}*F&f&N"
    "LXm&3jh^p*<PWq97oh*|RZvWkW5%OL595<^>t1toc0zmKAN1c-3hX1~m7x7kE8?3KCQ3t2&j!8{(bsG`oQ~Y`s?G$y`fkMEmlb-i"
    "1v1y;N!>AeX2^%aDfDpQ8`_}#d3ooS?}x3xH&-Y9^*-HLH#@8Z`13HnGVRBRNe6y0zqiNugiEUPC2d9KdI`zzqJq*7NIzW72fh!<"
    "-=LR23_bsI^*P{&A^w;PL2etmeSshMkvzXZw>f{eLO1YJtC1g%NZ80XTL}D3$QS*NDO1l!?*xACVzj5S57N(C6###)D(X)+_h?=^"
    "^bq)mS%_zQj-I@>lMVdSs24cidUG)3<WJyVM*rjXxx?mKNF?z8>EX+W9)27650LM=?LInt>f<8dzt~6G?@*BvoL0nKbCx1M9@bqj"
    "=cX3$1;dbk9Z$)$37-l4uKUP0tgHS^-5m`4uW6Vcvgv|@w&@e#|29K>cDc*^;`CAw$gM;^_49=H=ET(?P$K=K!Vj;`>FlLJFhZZS"
    "C%IOrvTn!$5U35HKfW&0^Qzqm1X{=^Tt~(a$b^@JKnL^Jk`fOEZpc~z0zF(`dY3bG#vcv^!4zU2=s5rBL*_*kgTTZP`NQ0cEs39}"
    "fxv8l{9Y%gJU>#R2ZC9oZW`^QHo|gj1#{n$)Ptl$XOupyV=n}OO$zd1O0Zcmu@3}xwz!{S<6do;lM4c8RkVkuVSj=?4h4Y=sdGjp"
    "o;Q3O_3Hr$+%Z1nbY^|rny1WtFVxGDydsuVcvXYIe<7~NJH{?swLL))qJjBO4UH2o8modJLV$QDYH@$vEv7%Q7s>l<&-orGUdg;K"
    "aSi5!l*^rPm-Pq1D#Qy3<N3C3KFss$6w$w|J$!@n!50MSFLAuD8vjmS%Zz_!G3o_5-E&soX8tcH5c^ZSbNp>n4G`?qM}0tUjEUJu"
    "W_$}Ue>0}kV6?*KWgyshk+e7L(v_gL4`V=3l8pBKQrv=7a1#Va$az|{LrRd$#qG@f<9+CVPg}L!xLpK-GpLUTnD)O8U7Zbri)%4H"
    "IN_>zfNKPT%DJSy(S?r}cSh@i;5z2VEsU5RXfVkf1XVZ4@1uWCb{sU_1OgiK3FBMX8H-|KK~RT!a%67dwTt)9f#5Of4`WaIownM*"
    "^#28^YfL5Yx^(qjZzc%dM4-J|U6FiW={X2E6Ob>}*qymAb_GF8GuofJPv7!1YeB%re4m7>#Kk%<G(jLiecRc2=JeK!O#ixupuOCk"
    "YweeN9R%-hqdh;lz(FgYneQ)2sORl?7tV8M*5eQKhY5!lWw;$z1HmBX%Pi`Su2V2c0HI7i=Et6IvbJdufKVRe^R85)sD9E$5Dr7W"
    "ne?A)@o({a5RN>J{&GUDZS~#@ARO(3eB$PspPx322jLhcjJJ$#n{V-odEa;v@1$b3zv#Cum<Ym2q~0=Z7R}k0Tq6TQLoMVx<ti!("
    "Lgw1!A;!~=nCCBWQ3c_2a-I<tweREI<wFcWIC}!-3udQ%xH!l>Z%OJJ(@tAj9u%rv1)&Y*Bf6Z5TcjPh6ohuDkHxh<xHBR)1%yuI"
    "TmUM{J~M8f0`q<s^ye|_OW%ynehNZ&<ZqD*&)QcRb%W5ej`TOYkKJ{C_iPaQA)oZK>G52pS_Z;kQg@zOVcaLaGR6{w;kPjU&EKAC"
    "<zWQEfAOP85<g<@C*b@Ad^tZMsP_;EQ%)mZ(MsBPv|A5^YcT(C;qu|9lMGlOT;GlPT1O6M$h@ls;U-eYlM0vD+|e7U0mAJ6P%rE4"
    "nrD^O3Bv6!k-x3m)^)*`8J}I`95X7U=jd?lD0L9-!FZI*!^mQv9$ygd$NlDEm;T~o)<X~;!u96;-_i{^u`fY*6!jS&^F;j^r%Vu@"
    "%tpTVGp%J*tsw}{O+<S>+p7G_-X$O`ug3e1NqJ8znEAiriTd5p>IZt0IUu}&`7r@L(o^r(j00gc<~Pr`JZ56?TN#A+$b3<=&WEf2"
    "bR7f2I$S@=E3FOg7X1X_6XH*(h??D1Z$F*|;R`9+pPk$ET|ec3@J%}AGukgXoc+rkgdCDjN*m|?eU+|h4#E~v=aC9)s`~2C8wNr?"
    "IY)w?bt7EGYf%~q#Td^tsdKkjxtf`ePJ#!iq!ioNHoblz?EOrxBjp`0HL83A;b)RRMJGndF5UO10EFL1qkj8f{FhY`%zO=?{^2uH"
    "y=08`Z4mxN{IsI3s9QyIK8WN<9YQLuvUGj(_3<E5BKf6s^!t$pL!KT5(QuMKONH&dn7GfK0+AZ>oyg#Cmd5Xx=QYVW33TAq85L&^"
    "6oF_Q(O>E4=nbOlYEwZpaX9I}^;@N~&r`R7XfioxgpPW&JHPU735bj^pWbh^_5IMfD?wz6_ABPL(<Z0J*&v!h@^Ppb`kvjE_PHRM"
    "L+XIiz8{wcC@akZkrg?YijKUyru;Y60wRjkfuzS9RbA1ymjRKz3%MV9tNw*<Pc?{~U!y+f)T@1HqXURsQNNF??N2mIT?iugX523a"
    "VmEmXQvi`y0OF$=AB)qJ)`G~d9r4O9bD3d_Hi9Ua;6FOTYTE5Rjf+7PE+p@d5h?F?DJ%t142d^VlkG?RdRq|+qIhzy9KCdE;3Wyy"
    "7epyxsNbDvP663^5Ty#p^IAz<^+PGl{H!PEB~alzu8iwRW5z$D72{JXIrB2=9YM6k7x9PlkGCJ-Hi)*dP_J^kx3T=507Q8h?+fT1"
    "B_BNW7l?LazOv&aqYJ5hPe4@Ui2mR+uk+y&X1q%7p+2B{?1lPcRS+Gq#C%ECkL4R?GV^sD^Od8*7fsn-Y6PM)Mi^f{F?k8Mr~yP5"
    "P+v*lsRmw{ybMH_wNRhFw&`^JF-s6#!+2Jr)bsf>b^(ZPqdkgPy&AkS$ARcB(X*(8g>&m12blF$OY-yS@H;D0opK^U^oZy~RB}a4"
    ";O}RDK=kxA?)Nem;kjg{|1Xg*MDNh*aHg34za{6tQTp$nw%j@E4x%Q^C$Rr~$@a}|W`0`tqy5!u*RNlC2Sfsl|3qC~qvp<z0FfjW"
    "`)4sYeY4M95dDkCI*@p5Gl<^1lj|gt8)v+GnEmpZM*FQHXQN)njK_Bqw9oGQo&L)o38Dc~FPDybbA&1#>I9;{r0y`4RCz-0(k}xL"
    "%i;Gc9)ohz^Ij@|SdrAnr~Sg(vulgmKs+4%W5oT?RQtbyAXYt3u4A`Gs2gkQgIH4?`OEZ2J@tj|ARdeP5+O@}v8?KgK&(sZr&2RN"
    "yH<DmmxEZJ<oi)^s-|ZwH>QBt5c6H4J5Swx((?qw(?+AczO{3{MfW)nPfx@3DH<1h_gEQ-XQ3V#_GiqFwvl^5Y)Q^fq9(oCeq@BC"
    "8N}9@Pv$&_Th1@?1@QtL-xUe3bhllT1+gQ>Ba*)LYK%H71L8#(@A3L5@ovm&0kIp#^Abyijaog-`<EeqjTw2tHb-qVh`l>;ywoa2"
    "jr_U`!~vL}HE|&I^Iy4I5Qm(`^<%mx<aebXh$HcP1KYUxPPPVfKNjPg)B7qD-m5eHNg(-dbgXB8Y3RAbAYQ4B{$piIQL5trh}R$<"
    "i;~S>qCSziUf=MKPv7+#@vI%ho2H_kQ*~6gC#M?3TL>SgP10gD<dZ`|yp4<FJ6fjUQr~b8=aD+=RP>E?`Je08gLpUcZ)J-P*CYDO"
    "eC-q9e0!UWJ^#=S#3dHU2VIj5y+<+QRf_n@^OyV7i|mUaE+gmfQ4Y?=ExiZLKz#aNd{;v+X0FXA5T7UKuhK~)FFQ|h=>%~FANfJz"
    "$IKIN5<q-)CiZ`Aj_;fQkH^iesMr1NcMQ?30dX}4@s#f8oDk&$Aig&h@v*ks*ywW<i0d%FI#Ac`()9NQAbw2dv*yj=zT~pmnIQg`"
    "zrVQq(N&99X1%_~_(zgl)ozX7^&n<lNBn(yPoKBXZV+>2(cToCmk$`^f|!TjKZK_&oqg<nE{KJtq<<?i+cSR7?E<m16R)k-1-hy2"
    "1aUXUPa@){2V`^afcOLElSjlZ%^SjE=IhH7)ceQ1jSRN$0Pzpx&v9)hj+d(1fOrt|@$4OIh9z390`cEdr2k>3rry`oqCg_oi~Kj|"
    "RJnsyB}kMo{^sX>VON3c3y=&adNt)Sr0T7sbs<PpYZ2e@l!Kj84M3ua`n65VrXxmHERc*P=cQ8dCjR`B!vjI0OU`SfW2*8!4j*;^"
    "$s}@47@c5ivQK;1ACMSgJSbqpi3Ydc3m`G^$NnGkKe#qt9VBMtdp<f`Z?kQqyAw!eV*XeBrH$pHJ}Zz|VEknH!*nZc<Ch?rAA<Yw"
    "w)w3;Mr|Mg)K3!?W|ZXQZv}}x$@iq98`e*}==%*M3lR@H9sKxoP|yq#SL9m(xzRQU44L-1A0p3(&AOxP4!I!l#P50R=gEgeoe2er"
    "A2}z1j&YiNfEI27Nf0@ogSOC#)L5c*4kZ8bAI$&dKS-kL$$YslxZ-Da_c}=8hM@i2`Pk8;a5zYkF#mV?n%<LZEKh-C725ByJ1_V>"
    "bF~G@+6v^4BTrazt(f`PAVqwB$K%eyNu?m!JiZq5llzkO9?O6vdpY8t?p*$Ab{9ytV}4+S`k#T7qlSVcuNL#E9Y%$gJDP)JH{zkl"
    "xf*WE8^4332<^X(wqSnCm@^<L2}XTdwrN@Ao>-8S?#1<>@hJVBQwm7R5WhI2YOpiD3qW!T^8*qqsXMY$?}6mJ3F4nO7t9V^-V2fn"
    "%y+UHSKPU`{tHO1;P(%UyAr2n-DK9!jT-ca=XH0jnve;SD$K9;H}P2c_*M}}XwqLg-k+6gz5fJA9w1%{Imgcl8@V1N^&~%>4xOb|"
    "?{+`~B+t&Ge_uA^c67KNNM0h|@R54GTWgmAl1B9BF}9=9Yf5O4H2sHq?iiIn;%UYpX(iteQL3jD-p#qkw1<!J4%@E6b~eujB;rem"
    "2Lyqf8F^YDd58Qo>{dW!X=MpWdWYctT{=1TfN2LvK9O^o>A9P>zgn<{Szmq2Fkk0c%9E_GWgzL_fP8IG|D%&9GoQbXBVR9gDcH<%"
    "1E~!9n-z0YX9pht1k#}&Fn%~iUh-~LKS+n+_dC9_uQ>;b*Mf8e=JUsB@@fu9wLq$dcqI1a+QX&W^FXSJ`3GTc^fUhMVvvqKh4}zZ"
    "xi7ednIP3A=Qz-@&u>>77LNq!q;8C7XRT0QHIN2UL;U_`h46t=Z*~PpO>q2HoU-y#%e4flnH&0_g0M)cKp&(tlkk4k_T_0~=Yn)@"
    "KK}mqD$PXcA&^>;^-ei;B!0PI;R;fU#8>I)a3$F-zsf*rN6ww5oagl2-IwnVQfJH`kBc8YjboDtQWuPm#YV@+dUw+xUAh4M>DC#("
    ">4jpDE+_ge9r1iq)1byKkou(I`WSmW{kV!5NCWmEU%9T*V4ZCa(vS+&Lw@%ul&od`KLW=i@on?$wNYO{8Y9H-UtO&akNeDwS3IeI"
    "Peon(dT_z`NRXzeV}IYTQEd1@fi%?w@#Vr@1@x7Akftp_J)$)ESQf7cq#J!vkK8-Hz3=>MkY?g|MSLk$F9vmxZpHlfWFK3HQEj6@"
    "ntKrS?!-B=Ur!Z+bQiYQGivzzqb)ihExeE8YtuBp>-rOr7O^pYSbk6LQgSayOFEI?&AdUiB{Tgg9Yp&guf0X7Y9UCEBmZ4~>#yH;"
    "0khstPr!W9!I1fR#i}4ZKOOaEh)*3%*ap%HTQYvW@s!{9<(?qD;*R=Nw6gqcF>`$b?e#+G_409Z1t6_T!hFGs_5QUD%=>CGFyC&*"
    "<FQXhGXH;{oPS3ro4vO3(NY8HBm7>`f8U)u{_-r4J|+B=Uam9cM$eP+AZ@sUcsxNna@TheNdM&{X^?y*J&>}WB0u(t{G{t$3Q{im"
    "r}<~bd~W53f|Q4RDMsVq<aJa5NQLO1LwoX^J0`Y*RQfp+^AY=xx;|mnPuBoGKj@RAU6}#W53;ykTf27dHvSIMFUpwDB>8Ca=f8&_"
    "{jP@Jf2gj_kV#_ZXMpI#ROqk9nHvi)fb<WJZ`_+5WAcNHphMQ67Ws)0%OZa@bSU8ZiTZF$wm|bPbSRsly|X)EFh<u4I!4YyJvHTn"
    "Tf9Oqbg0io{}XaFtX8oPI<%}%51mB$Ppf5qKhB!mw;AD9JLl^;=$L@tbI)vRdv2fP3my8Xw;Bg`y>dCD2OWl(-#S?_@AVf&Rp>Cm"
    "{6W1dbojHAmHz|dPspS"
)
_FAST_TABLES = _fast_struct.unpack(
    ">7098d", _fast_zlib.decompress(_fast_base64.b85decode(_FAST_TABLE_DATA))
)
_FAST_EXP_INT_A = _FAST_TABLES[:1500]
_FAST_EXP_INT_B = _FAST_TABLES[1500:3000]
_FAST_EXP_FRAC_A = _FAST_TABLES[3000:4025]
_FAST_EXP_FRAC_B = _FAST_TABLES[4025:5050]
_FAST_LN_MANT = _FAST_TABLES[5050:]
del _FAST_TABLE_DATA, _FAST_TABLES

_FAST_LN_QUICK_COEF = (
    (1.0, 5.669184079525e-24),
    (-0.25, -0.25),
    (0.3333333134651184, 1.986821492305628e-8),
    (-0.25, -6.663542893624021e-14),
    (0.19999998807907104, 1.1921056801463227e-8),
    (-0.1666666567325592, -7.800414592973399e-9),
    (0.1428571343421936, 5.650007086920087e-9),
    (-0.12502530217170715, -7.44321345601866e-11),
    (0.11113807559013367, 9.219544613762692e-9),
)
_FAST_LN_HI_PREC_COEF = (
    (1.0, -6.032174644509064e-23),
    (-0.25, -0.25),
    (0.3333333134651184, 1.9868161777724352e-8),
    (-0.2499999701976776, -2.957007209750105e-8),
    (0.19999954104423523, 1.5830993332061267e-10),
    (-0.16624879837036133, -2.6033824355191673e-8),
)


def _fast_log_poly(
    xa: float, xb: float, coefficients: tuple[tuple[float, float], ...]
) -> tuple[float, float]:
    """Evaluate FastMath's split-double logarithm polynomial."""
    ya, yb = coefficients[-1]
    for ca, cb in reversed(coefficients[:-1]):
        aa = ya * xa
        ab = ya * xb + yb * xa + yb * xb
        tmp = aa * 1073741824.0
        ya = aa + tmp - tmp
        yb = aa - ya + ab
        aa = ya + ca
        ab = yb + cb
        tmp = aa * 1073741824.0
        ya = aa + tmp - tmp
        yb = aa - ya + ab
    return ya * xa, ya * xb + yb * xa + yb * xb


def _fast_log_internal(x: float, hi_prec: list[float] | None = None) -> float:
    """Port of FastMath.log(double, double[]), including split output."""
    if x == 0.0:
        return float("-inf")
    bits = _fast_struct.unpack(">Q", _fast_struct.pack(">d", x))[0]
    if bits & 0x8000000000000000 or x != x:
        if hi_prec is not None:
            hi_prec[0] = float("nan")
        return float("nan")
    if x == float("inf"):
        if hi_prec is not None:
            hi_prec[0] = x
        return x
    exponent = (bits >> 52) - 1023
    if bits & 0x7FF0000000000000 == 0:
        bits <<= 1
        while bits & 0x0010000000000000 == 0:
            exponent -= 1
            bits <<= 1
    if exponent in (-1, 0) and 0.99 < x < 1.01 and hi_prec is None:
        xa = x - 1.0
        tmp = xa * 1073741824.0
        aa = xa + tmp - tmp
        xb = xa - aa
        xa = aa
        aa, ab = _fast_log_poly(xa, xb, _FAST_LN_QUICK_COEF)
        tmp = aa * 1073741824.0
        ya = aa + tmp - tmp
        yb = aa - ya + ab
        return ya + yb
    mantissa_index = ((bits & 0x000FFC0000000000) >> 42) * 2
    lnm_a = _FAST_LN_MANT[mantissa_index]
    lnm_b = _FAST_LN_MANT[mantissa_index + 1]
    numer = float(bits & 0x3FFFFFFFFFF)
    denom = 4503599627370496.0 + (bits & 0x000FFC0000000000)
    epsilon = numer / denom
    lnzb = 0.0
    if hi_prec is not None:
        tmp = epsilon * 1073741824.0
        xa = epsilon + tmp - tmp
        xb = epsilon - xa
        aa = numer - xa * denom - xb * denom
        xb += aa / denom
        aa, ab = _fast_log_poly(xa, xb, _FAST_LN_HI_PREC_COEF)
        lnza = aa + ab
        lnzb = -(lnza - aa - ab)
    else:
        lnza = -0.16624882440418567
        lnza = lnza * epsilon + 0.19999954120254515
        lnza = lnza * epsilon + -0.2499999997677497
        lnza = lnza * epsilon + 0.3333333333332802
        lnza = lnza * epsilon + -0.5
        lnza = lnza * epsilon + 1.0
        lnza *= epsilon
    a = 0.693147063255310059 * exponent
    b = 0.0
    for term in (lnm_a, lnza, 1.17304635250823482e-7 * exponent, lnm_b, lnzb):
        c = a + term
        d = -(c - a - term)
        a = c
        b += d
    if hi_prec is not None:
        hi_prec[0] = a
        hi_prec[1] = b
    return a + b


def _fast_log(x: float) -> float:
    """Apache Commons Math 3.6.1 FastMath.log, with binary64 operation order."""
    return _fast_log_internal(x)


def _fast_log1p(x: float) -> float:
    """Apache Commons Math 3.6.1 FastMath.log1p."""
    if x == -1.0:
        return float("-inf")
    if x == float("inf"):
        return x
    if x > 1e-6 or x < -1e-6:
        xpa = 1.0 + x
        xpb = -(xpa - 1.0 - x)
        hi_prec = [0.0, 0.0]
        lores = _fast_log_internal(xpa, hi_prec)
        if lores == float("inf") or lores == float("-inf"):
            return lores
        fx1 = xpb / xpa
        epsilon = 0.5 * fx1 + 1.0
        return epsilon * fx1 + hi_prec[1] + hi_prec[0]
    y = (x * (1.0 / 3.0) - 0.5) * x + 1.0
    return y * x


def _fast_exp(x: float) -> float:
    """Apache Commons Math 3.6.1 FastMath.exp, including subnormal outputs."""
    if x != x:
        return float("nan")
    if x < -746.0:
        return 0.0
    if x >= 710.0:
        return float("inf")
    int_val = int(x)
    if x < 0.0:
        if int_val < -709:
            return _fast_exp(x + 40.19140625) / 285040095144011776.0
        if int_val == -709:
            return _fast_exp(x + 1.494140625) / 4.455505956692756620
        int_val -= 1
    int_a = _FAST_EXP_INT_A[750 + int_val]
    int_b = _FAST_EXP_INT_B[750 + int_val]
    int_frac = int((x - int_val) * 1024.0)
    frac_a = _FAST_EXP_FRAC_A[int_frac]
    frac_b = _FAST_EXP_FRAC_B[int_frac]
    epsilon = x - (int_val + int_frac / 1024.0)
    z = 0.04168701738764507
    z = z * epsilon + 0.1666666505023083
    z = z * epsilon + 0.5000000000042687
    z = z * epsilon + 1.0
    z = z * epsilon + -3.940510424527919e-20
    temp_a = int_a * frac_a
    temp_b = int_a * frac_b + int_b * frac_a + int_b * frac_b
    temp_c = temp_b + temp_a
    if temp_c == float("inf"):
        return temp_c
    return temp_c * z + temp_b + temp_a


# Derived from Apache Commons Math 3.6.1 (Apache License 2.0).
# Copyright The Apache Software Foundation. Original source: special/Erf.java,
# special/Gamma.java and util/ContinuedFraction.java; see the Apache NOTICE.
# The coefficients below are original primary-source algorithm data, not golden values.
# Combine with the exact FastMath support in growth_chart.py; no runtime Java needed.


_ERF_INV_A: tuple[float, ...] = (
    -3.64441206401782e-21,
    -1.6850591381820166e-19,
    1.28584807152564e-18,
    1.1157877678025181e-17,
    -1.333171662854621e-16,
    2.0972767875968562e-17,
    6.637638134358324e-15,
    -4.054566272975207e-14,
    -8.151934197605472e-14,
    2.6335093153082323e-12,
    -1.2975133253453532e-11,
    -5.415412054294628e-11,
    1.0512122733215323e-09,
    -4.112633980346984e-09,
    -2.9070369957882005e-08,
    4.2347877827932404e-07,
    -1.3654692000834679e-06,
    -1.3882523362786469e-05,
    0.00018673420803405714,
    -0.000740702534166267,
    -0.006033670871430149,
    0.24015818242558962,
    1.6536545626831027,
)
_ERF_INV_B: tuple[float, ...] = (
    2.2137376921775787e-09,
    9.075656193888539e-08,
    -2.7517406297064545e-07,
    1.8239629214389228e-08,
    1.5027403968909828e-06,
    -4.013867526981546e-06,
    2.9234449089955446e-06,
    1.2475304481671779e-05,
    -4.7318229009055734e-05,
    6.828485145957318e-05,
    2.4031110387097894e-05,
    -0.0003550375203628475,
    0.0009532893797373805,
    -0.0016882755560235047,
    0.002491442096107851,
    -0.003751208507569241,
    0.005370914553590064,
    1.0052589676941592,
    3.0838856104922208,
)
_ERF_INV_C: tuple[float, ...] = (
    -2.7109920616438573e-11,
    -2.555641816996525e-10,
    1.5076572693500548e-09,
    -3.789465440126737e-09,
    7.61570120807834e-09,
    -1.496002662714924e-08,
    2.914795345090108e-08,
    -6.771199775845234e-08,
    2.2900482228026655e-07,
    -9.9298272942317e-07,
    4.526062597223154e-06,
    -1.968177810553167e-05,
    7.599527703001776e-05,
    -0.00021503011930044477,
    -0.00013871931833623122,
    1.0103004648645344,
    4.849906401408584,
)
_GAMMA_HALF_A: tuple[float, ...] = (6.116095104481416e-09, 6.247308301164655e-09)
_GAMMA_HALF_B: tuple[float, ...] = (
    1.9575583661463974e-10,
    -6.077618957228252e-08,
    9.926418406727737e-07,
    -6.4304548177935305e-06,
    -8.514194324403149e-06,
    0.0004939449793824468,
    0.026620534842894922,
    0.203610414066807,
)
_GAMMA_HALF_C: tuple[float, ...] = (
    -2.056338416977607e-07,
    1.133027231981696e-06,
    -1.2504934821426706e-06,
    -2.013485478078824e-05,
    0.0001280502823881162,
    -0.00021524167411495098,
    -0.0011651675918590652,
    0.0072189432466631,
    -0.009621971527876973,
    -0.04219773455554433,
    0.16653861138229148,
    -0.04200263503409524,
    -0.6558780715202539,
    -0.42278433509846713,
)


@lru_cache(maxsize=1)
def _log_gamma_half() -> float:
    """Java: Gamma#logGamma(0.5) -> logGamma1p(-0.5); preserve its DGAM1 path."""
    t = -0.5
    a = _GAMMA_HALF_A[0] + t * _GAMMA_HALF_A[1]
    b = _GAMMA_HALF_B[0]
    for coefficient in _GAMMA_HALF_B[1:]:
        b = coefficient + t * b
    b = 1.0 + t * b
    c = _GAMMA_HALF_C[0] + t * (a / b)
    for coefficient in _GAMMA_HALF_C[1:]:
        c = coefficient + t * c
    inv_gamma = t * ((c + 0.5) + 0.5)
    return -_fast_log1p(inv_gamma)


def _gamma_half_p(x: float) -> float:
    """Java: Gamma#regularizedGammaP(0.5,x,1e-15,10000), the erfc branch."""
    if math.isnan(x) or x < 0.0:
        return math.nan
    if x == 0.0:
        return 0.0
    if x >= 1.5:
        return 1.0 - _gamma_half_q(x)
    n, an, total = 0.0, 2.0, 2.0
    while abs(an / total) > 1e-15 and n < 10000 and total < math.inf:
        n += 1.0
        an *= x / (0.5 + n)
        total += an
    if n >= 10000:
        raise ArithmeticError("Gamma series failed to converge after 10000 iterations")
    if math.isinf(total):
        return 1.0
    return _fast_exp(-x + (0.5 * _fast_log(x)) - _log_gamma_half()) * total


def _gamma_half_q(x: float) -> float:
    """Java: Gamma#regularizedGammaQ(0.5,x,1e-15,10000), including continued fraction."""
    if math.isnan(x) or x < 0.0:
        return math.nan
    if x == 0.0:
        return 1.0
    if x < 1.5:
        return 1.0 - _gamma_half_p(x)
    # Java: ContinuedFraction#evaluate (modified Lentz), exact evaluation order.
    small = 1e-50
    h_prev = ((2.0 * 0) + 1.0) - 0.5 + x
    if abs(h_prev) <= small:
        h_prev = small
    n, d_prev, c_prev = 1, 0.0, h_prev
    h_n = h_prev
    while n < 10000:
        a = ((2.0 * n) + 1.0) - 0.5 + x
        b = n * (0.5 - n)
        d_n = a + b * d_prev
        if abs(d_n) <= small:
            d_n = small
        c_n = a + b / c_prev
        if abs(c_n) <= small:
            c_n = small
        d_n = 1.0 / d_n
        delta_n = c_n * d_n
        h_n = h_prev * delta_n
        if not math.isfinite(h_n):
            raise ArithmeticError("Gamma continued fraction diverged")
        if abs(delta_n - 1.0) < 1e-15:
            break
        d_prev, c_prev, h_prev = d_n, c_n, h_n
        n += 1
    if n >= 10000:
        raise ArithmeticError("Gamma continued fraction failed after 10000 iterations")
    result = 1.0 / h_n
    return _fast_exp(-x + (0.5 * _fast_log(x)) - _log_gamma_half()) * result


def _erfc(x: float) -> float:
    """Java: Erf#erfc, using the exact regularized gamma algorithms."""
    if abs(x) > 40.0:
        return 0.0 if x > 0.0 else 2.0
    result = _gamma_half_q(x * x)
    return 2.0 - result if x < 0.0 else result


def _erf_inv(x: float) -> float:
    """Java: Erf#erfInv (Giles polynomial); never replace (1-x)*(1+x) with 1-x*x."""
    w = -_fast_log((1.0 - x) * (1.0 + x))
    if w < 6.25:
        w -= 3.125
        coefficients = _ERF_INV_A
    elif w < 16.0:
        w = math.sqrt(w) - 3.25
        coefficients = _ERF_INV_B
    elif not math.isinf(w):
        w = math.sqrt(w) - 5.0
        coefficients = _ERF_INV_C
    else:
        return math.inf * x
    p = coefficients[0]
    for coefficient in coefficients[1:]:
        p = coefficient + p * w
    return p * x


def _erfc_inv(x: float) -> float:
    """Java: Erf#erfcInv."""
    return _erf_inv(1.0 - x)


def _normal_cdf(x: float) -> float:
    """Java: NormalDistribution(0,1)#cumulativeProbability, including extreme tails."""
    dev = x - 0.0
    if abs(dev) > 40.0 * 1.0:
        return 0.0 if dev < 0.0 else 1.0
    return 0.5 * _erfc(-dev / (1.0 * math.sqrt(2.0)))


def _normal_ppf(p: float) -> float:
    """Java: NormalDistribution(0,1)#inverseCumulativeProbability (not GrowthChart's z-score)."""
    if p < 0.0 or p > 1.0:
        raise ValueError("Probability must be in [0,1]")
    return 0.0 + 1.0 * math.sqrt(2.0) * _erf_inv(2.0 * p - 1.0)
