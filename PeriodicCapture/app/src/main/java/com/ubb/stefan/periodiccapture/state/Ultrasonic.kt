package com.ubb.stefan.periodiccapture.state

class Ultrasonic
{
    private var distance:Int=Int.MAX_VALUE

    fun isCovered():Boolean
    {
        return this.distance < 5
    }
}