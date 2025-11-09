START 100
LOOP    MOVER    AREG, ='5'
        ADD      BREG, ONE
        SUB      CREG, ='2'
ONE     DC       1
        LTORG
        ORIGIN   110
        MOVEM   AREG, TWO
TWO     DS      2
        END
