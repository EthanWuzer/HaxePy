from enum import Enum

TokenType = Enum("TokenType",
                "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE\
                    COMMA DOT MINUS PLUS SEMICOLON SLASH STAR QUESTION\
                        BANG BANG_EQUAL\
                            EQUAL EQUAL_EQUAL\
                                LESS LESS_EQUAL\
                                    IDENTIFIER STRING NUMBER\
                                        AND ELSE FALSE FOR IF NULL OR\
                                            PRINT RETURN TRUE WHILE BREAK\
                                                EOF")