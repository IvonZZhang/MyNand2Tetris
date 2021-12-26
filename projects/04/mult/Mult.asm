// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.

// (init)
//     Loopi = 0
//     Loopn = R0
//     if i >= n:
//         jump to end
//     D += R1
//     jump to loop
// (end)
//     R2 = D


    @i      // i = 0
    M = 0
    @R0     // n = R0
    D = M
    @n
    M = D
    @sum    // sum = 0
    M = 0
(loop)
    @i      // D = i - n
    D = M
    @n
    D = D-M
    @end
    D;JGE   // if (i-n >= 0) Jump to end
    @R1
    D = M
    @sum
    M = D+M // sum += R1
    @i
    M = M+1 // i++
    @loop
    0;JMP
(end)
    @sum
    D = M
    @R2
    M = D
    @fin
    0;JMP