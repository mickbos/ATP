#include <Arduino.h>
#include <unity.h>
extern "C"
{
    void serialBegin()
    {
        Serial.begin(9600);
    }

    void printStr(const char *str)
    {
        Serial.print(str);
    }

    void printlnStr(const char *str)
    {
        Serial.println(str);
    }

    void printInteger(int i)
    {
        Serial.print(i);
    }

    void printlnInteger(int i)
    {
        Serial.println(i);
    }

    bool odd(int i);
    bool even(int i);
    int sommig(int i);
    int add(int a, int b);
    int subtract(int a, int b);
}
unsigned int sommigReference(unsigned int n) // copied from the reader to use as reference
{
    unsigned int result = 0;
    while (n >= 1)
    {
        result += n;
        n--;
    }
    return result;
}

void testOdd()
{
    TEST_ASSERT_EQUAL(true, odd(5));
    TEST_ASSERT_EQUAL(true, odd(27));
    TEST_ASSERT_EQUAL(true, odd(1233));
    TEST_ASSERT_EQUAL(false, odd(0));
    TEST_ASSERT_EQUAL(false, odd(24));
    TEST_ASSERT_EQUAL(false, odd(1232));
}

void testEven()
{
    TEST_ASSERT_EQUAL(false, even(5));
    TEST_ASSERT_EQUAL(false, even(27));
    TEST_ASSERT_EQUAL(false, even(1233));
    TEST_ASSERT_EQUAL(true, even(0));
    TEST_ASSERT_EQUAL(true, even(24));
    TEST_ASSERT_EQUAL(true, even(1232));
}

void testSommig()
{
    for (int i = 0; i < 2000; i++)
    {
        TEST_ASSERT_EQUAL(sommigReference(i), sommig(i));
    }
}

void testAdd()
{
    TEST_ASSERT_EQUAL(10, add(5, 5)); // equal
    TEST_ASSERT_EQUAL(5, add(5, 0));  // rhs zero 
    TEST_ASSERT_EQUAL(5, add(0, 5));  // lhs zero
    TEST_ASSERT_EQUAL(0, add(0, 0));  // both zero
    TEST_ASSERT_EQUAL(6, add(1, 5));  // a < b
    TEST_ASSERT_EQUAL(6, add(5, 1));  // a > b
}

void testSubtract()
{
    TEST_ASSERT_EQUAL(0, subtract(5, 5)); // equal
    TEST_ASSERT_EQUAL(5, subtract(5, 0));  // rhs zero 
    TEST_ASSERT_EQUAL(-5, subtract(0, 5));  // lhs zero
    TEST_ASSERT_EQUAL(0, subtract(0, 0));  // both zero
    TEST_ASSERT_EQUAL(-4, subtract(1, 5));  // a < b
    TEST_ASSERT_EQUAL(4, subtract(5, 1));  // a > b
}

void setup()
{
    Serial.begin(9600);       // Needed to be able to print to serial monitor
    Sleep(1000);
    UNITY_BEGIN();
        // testing basic operators
    RUN_TEST(testAdd);
    RUN_TEST(testSubtract);
//     // testing examples, functioncalls
    RUN_TEST(testOdd);
    RUN_TEST(testEven);
    RUN_TEST(testSommig); // C:\Users\mickb\.platformio\penv\Scripts\platformio.exe
    
    UNITY_END();
}

void loop()
{
    // Arduino gets big mad without this function
}