#ifndef CLASS_TEST
#define CLASS_TEST

template <class T>
class Class_test{
    private:
    T m_a;
    T m_b;

    public:
    Class_test();
    Class_test(T, T);
    T multiplier();
};

#endif
