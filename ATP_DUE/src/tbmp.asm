.cpu cortex-m0

.global subtract 
.global add 
.global even 
.global odd 
.global sommig 
subtract:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	str r1, [r7, #8]
	ldr r2, [r7, #4]
	ldr r3, [r7, #8]
	sub r0, r2, r3
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
add:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	str r1, [r7, #8]
	ldr r2, [r7, #4]
	ldr r3, [r7, #8]
	add r0, r2, r3
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
even:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	ldr r2, [r7, #4]
	mov r3, #0
	cmp r2, r3
	bne .L1
	mov r0, #1
	b .L2
.L1:
	ldr r2, [r7, #4]
	mov r3, #1
	sub r2, r2, r3
	mov r0, r2
	bl odd
	mov r0, r0
.L2:
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
odd:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	ldr r2, [r7, #4]
	mov r3, #0
	cmp r2, r3
	bne .L3
	mov r0, #0
	b .L4
.L3:
	ldr r2, [r7, #4]
	mov r3, #1
	sub r2, r2, r3
	mov r0, r2
	bl even
	mov r0, r0
.L4:
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
sommig:
	push {r7, lr}
	sub sp, sp, #16
	add r7, sp, #0
	str r0, [r7, #4]
	bl printlnInteger
	mov r2, #0
	str r2, [r7, #8]
.L5:
	ldr r2, [r7, #4]
	mov r3, #0
	cmp r2, r3
	ble .L6
	ldr r2, [r7, #8]
	ldr r3, [r7, #4]
	add r2, r2, r3
	str r2, [r7, #8]
	ldr r2, [r7, #4]
	mov r3, #1
	sub r2, r2, r3
	str r2, [r7, #4]
	b .L5
.L6:
	ldr r0, [r7, #8]
	mov sp, r7
	add sp, sp, #16
	pop {r7, pc}
