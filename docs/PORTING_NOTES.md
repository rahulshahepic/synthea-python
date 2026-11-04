# Porting notes (append-only)

Record intentional deviations, reproduced Java quirks and suspected precision issues here.
Format (see PORTING_GUIDE §9):

```
## #<issue> <Class> (agent: <name>)
- <what and why>
```

## #1 JavaRandom and DefaultRandomNumberGenerator (agent: chatgpt)
- `java.util.Random#nextLong` sign-extends each 32-bit draw before adding the low word; combining unsigned halves changes results.
- `java.util.Random#nextGaussian` requires the fdlibm 5.3 implementation of `StrictMath.log` for exact parity. Platform `math.log` differs by up to an ulp on observed seeded trajectories; `random.py` includes the permissively licensed fdlibm polynomial with its notice preserved.
- `DefaultRandomNumberGenerator#randUUID` constructs the UUID from the original seed and one counted `randLong` draw (not four random words).
