package com.ubb.stefan.myparking.model

import java.util.*

class PlateEntry: Comparable<PlateEntry> {
    var id: String? = null
    var user: String? = null
    var plate: String? = null
    var time: Date? = null

    constructor() {}
    constructor(id: String, user: String, plate: String, time: Date)
    {
        this.id = id;
        this.user = user
        this.plate = plate
        this.time = time
    }
    constructor(plate: String, time: Date)
    {
        this.plate = plate
        this.time = time
    }

    override fun compareTo(other: PlateEntry) =
        time!!.compareTo(other.time)


    override fun toString(): String {
        return "Plate:"+this.plate+" at "+this.time+" for user with id "+this.user
    }
}
