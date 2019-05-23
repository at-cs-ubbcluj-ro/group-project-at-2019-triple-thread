package com.ubb.stefan.periodiccapture.state

class Context
{
    lateinit var ultrasonic: Ultrasonic

    private lateinit var currentState:State
    fun getNext()
    {
        currentState.getNext(this)
    }

}