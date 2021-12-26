// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

// HACK SCREEN contains 256 rows with 512 (32 * 16) pixels in each row

// (init)
// res = check key
// if not res:
//     goto init
// blacken the screen
// (init2)
// res = check key
// if res:
//     goto init2
// whiten the screen
// goto init


    @isBlack// isBlack = False
    M = 0

(WHITE)
    @KBD
    D = M
    @WHITE
    D;JEQ   // if (KBD == 0) keep checking; else go blacken the screen
    @isBlack
    M = 0   // isBlack = False
    @OPSCREEN
    0;JMP

(BLACK)
    @KBD
    D = M
    @BLACK
    D;JNE   // if (KBD != 0) keep checking; else go whiten the screen
    @isBlack
    M = 1   // isBlack = True
    @OPSCREEN
    0;JMP

(OPSCREEN)
    @SCREEN
    D = A
    @addr
    M = D   // addr = SCREEN
    @rowcount
    M = 0   // rowcount = 0
    @256
    D = A
    @totalrow
    M = D   // totalrow = 256 (rows)
(LOOP)
    @i
    M = 0   // i = 0
    @32
    D = A
    @n
    M = D   // n = 32 (32 words in a row)
    (ROWLOOP)
        @isBlack
        D = M
            @makeblack
            D;JEQ
            @makewhite
            D;JNE
            (makeblack)
            @addr
            A = M
            M = -1  // RAM[addr] = -1 (a word == 16 bits)
            @makeend
            0;JMP
            (makewhite)
            @addr
            A = M
            M = 0
            (makeend)
        @addr
        M = M+1 // addr += 1
        @i
        M = M+1 // i++
        D = M
        @n
        D = D-M
        @ENDROWLOOP
        D;JGE   // if (i-n >= 0) goto ENDROWLOOP
        @ROWLOOP
        0;JMP
    (ENDROWLOOP)
    @rowcount
    M = M+1 // rowcount++
    D = M
    @totalrow
    D = D-M
    @END
    D;JGE   // if (rowcount - totalrow >= 0) goto END
    @LOOP
    0;JMP
(END)
    @isBlack
    D = M   // D = isBlack
    @BLACK
    D;JEQ   // if (isBlack) goto BLACK
    @WHITE
    D;JNE   // if (!isBlack) goto WHITE