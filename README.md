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

```java
testgroup add
```

After defining a testgroup, an `expected`/`actual` pair defines a test.

```java
expected = 5
actual = 2, 3
```

The value of `actual` is determined by calling the testgroup method with the arguments following the assignment operator.

### Equators

Some tests will compare objects whose equivalences cannot be determined with the usual `equals(Object)`. For cases such as this, Equators can be defined.

```java
equator arrayEquator = equate(Object a, Object b) { return Arrays.equals((int[])a, (int[])b); }
```

To override the Equator used for a particular test, reassign `equator`.

```java
testgroup dotProduct

equator = arrayEquator
expected = new double[] {1.0, 3.5, -0.7}
actual = new double[] {1.0, 0.5, 0.35}, new double[] {1.0, 7.0, -2.0}
```

### Translators

The auto-generated `runTest` method will print string representations of the expected and actual values. In cases where the default `toString()` is not preferable, Translators can be used to overwrite it.

 ```java
 translator arrayTranslator = translate(Object obj) { return Arrays.toString((int[])obj); }

 ...

 translator = arrayTranslator
 ```

 ### Put it all together

`example.txt`
 ```java
 import java.util.Arrays;

 equator arrayEquator = equate(Object a, Object b) { return Arrays.equals((int[])a, (int[])b); }
 translator arrayTranslator = translate(Object obj) { return Arrays.toString((int[])obj); }

testgroup dotProduct

equator = arrayEquator
translator = arrayTranslator
expected = new double[] {1.0, 3.5, -0.7}
actual = new double[] {1.0, 0.5, 0.35}, new double[] {1.0, 7.0, -2.0}
```

This will generate the following file:

`ExampleTester.java`
```java
import java.util.Arrays;

public class InputTester {
	private interface Equator {
		public abstract boolean equate(Object a, Object b);
	}
	private interface Translator {
		public abstract String translate(Object obj);
	}
	private static Equator defaultEquator = new Equator() {
		@Override public boolean equate(Object a, Object b) {
			return a.equals(b);
		}
	};
	private static Translator defaultTranslator = new Translator() {
		@Override public String translate(Object obj) {
			return obj.toString();
		}
	};
	private static Equator arrayEquator = new Equator() {
		@Override public boolean equate(Object a, Object b) {
			return Arrays.equals((int[])a, (int[])b);
		}
	};
	private static Translator arrayTranslator = new Translator() {
		@Override public String translate(Object obj) {
			return Arrays.toString((int[])obj);
		}
	};

	public static void main(String[] args) {
		Object expected, actual;
		String testName = "";
		double testNum = 1;

		// dotProduct tests
		testName = "dotProduct";
		testNum = Math.floor(testNum) + 1;

		expected = new double[] {1.0, 3.5, -0.7};
		actual = dotProduct(new double[] {1.0, 0.5, 0.35}, new double[] {1.0, 7.0, -2.0});
		runTest(testNum, testName, expected, actual, arrayEquator, arrayTranslator);
		testNum += 0.1;
	}

	private static void runTest(double testNum, String testName, Object expected, Object actual, Equator equator, Translator translator) {
		boolean equivalent = equator.equate(expected, actual);
		String testLevel = "" + (testNum % 1 == 0 ? (int)testNum : testNum);
		String result = (equivalent ? "Passed" : "**FAILED") + " Test " + testLevel;

		System.out.println("Test " + testLevel + ": " + testName + "\n" +
			"Expected value: " + translator.translate(expected) + "\n" +
			"Received value: " + translator.translate(actual) + "\n" +
			result);
	}
}
```

The method being tested (`dotProduct`) would of course need to be implemented by the user.

## Dependencies

* Python 3
