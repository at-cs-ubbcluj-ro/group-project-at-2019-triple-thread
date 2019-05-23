package com.ubb.stefan.myparking.adapter


import android.content.Context
import android.support.v7.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView

import com.google.firebase.firestore.FirebaseFirestore

import com.ubb.stefan.myparking.R
import com.ubb.stefan.myparking.model.PlateEntry
import java.text.SimpleDateFormat
import java.util.*


class PlateHistoryRecyclerViewAdapter(
    private val platesEntries: MutableList<PlateEntry>,
    private val context: Context,
    private val firestoreDB: FirebaseFirestore)
    : RecyclerView.Adapter<PlateHistoryRecyclerViewAdapter.ViewHolder>() {


    fun getPlates():MutableList<PlateEntry>{
        return this.platesEntries
    }
    fun sortList(){
        platesEntries.sort()
        notifyDataSetChanged()
    }
    fun reverseList(){
        platesEntries.reverse()
        notifyDataSetChanged()
    }
    override fun onCreateViewHolder(p0: ViewGroup, p1: Int): ViewHolder  {
        val view = LayoutInflater.from(p0.context).inflate(R.layout.plate_entry, p0, false)

        return ViewHolder(view)
    }

    override fun onBindViewHolder(p0: ViewHolder, p1: Int) {
        val plateEntry = platesEntries[p1]

        p0.plate.text = plateEntry.plate
        val dateFormat = SimpleDateFormat("yyyy-MM-dd hh:mm")
        val strDate = dateFormat.format(plateEntry.time)
        p0.timestamp.text = strDate
    }

    override fun getItemCount(): Int {
        return platesEntries.size
    }

    inner class ViewHolder internal constructor(view: View) : RecyclerView.ViewHolder(view) {
        //internal var user: TextView
        internal var plate:TextView = view.findViewById(R.id.tvPlate)
        internal var timestamp: TextView = view.findViewById(R.id.tvTimestamp)

    }

}