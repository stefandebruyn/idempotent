# idempotent

A tool for generating Java test cases. Written for use in UT Austin's CS 314 Data Structures class, which puts emphasis on test thoroughness and disallows testing frameworks.

`C:\>py idempotent.py <input_file>`

## Writing the Input Files

### Imports

Begin the source with required imports. Complete Java syntax is required; these are copied directly into the generated file.

```
import java.util.Arrays;
```

### Testgroups

A testgroup is a series of tests that test the same method. The following line defines a testgroup for the method `shift(...)`.

```
testgroup add
```

After defining a testgroup, an `expected`/`actual` pair defines a test.

```
expected = 5
actual = 2, 3
```

The value of `actual` is determined by calling the testgroup method with the arguments following the assignment operator.

### Equators

Some tests will compare objects whose equivalences cannot be determined with the usual `equals(Object)`. For cases such as this, Equators can be defined.

```
equator arrayEquator = equate(Object a, Object b) { return Arrays.equals((int[])a, (int[])b); }
```

To override the Equator used for a particular test, reassign `equator`.

```
testgroup dotProduct

equator = arrayEquator
expected = new double[] {1.0, 3.5, -0.7}
actual = new double[] {1.0, 0.5, 0.35}, new double[] {1.0, 7.0, -2.0}
```

### Translators

The auto-generated `runTest` method will print string representations of the expected and actual values. In cases where the default `toString()` is not preferable, Translators can be used to overwrite it.

 ```
 translator arrayTranslator = translate(Object obj) { return Arrays.toString((int[])obj); }

 ...

 translator = arrayTranslator
 ```

 ### Put it all together

 ```
 import java.util.Arrays;

 equator arrayEquator = equate(Object a, Object b) { return Arrays.equals((int[])a, (int[])b); }
 translator arrayTranslator = translate(Object obj) { return Arrays.toString((int[])obj); }

testgroup dotProduct

equator = arrayEquator
translator = arrayTranslator
expected = new double[] {1.0, 3.5, -0.7}
actual = new double[] {1.0, 0.5, 0.35}, new double[] {1.0, 7.0, -2.0}
```
