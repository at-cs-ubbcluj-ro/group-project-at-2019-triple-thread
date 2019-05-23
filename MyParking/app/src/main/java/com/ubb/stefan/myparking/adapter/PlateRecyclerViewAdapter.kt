package com.ubb.stefan.myparking.adapter

import android.content.Context
import android.support.v7.widget.RecyclerView
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast

import com.google.firebase.firestore.FirebaseFirestore

import com.ubb.stefan.myparking.R
import com.ubb.stefan.myparking.model.PlateEntry


class PlateRecyclerViewAdapter(
    private val platesEntries: MutableList<PlateEntry>,
    private val context: Context,
    private val firestoreDB: FirebaseFirestore)
    : RecyclerView.Adapter<PlateRecyclerViewAdapter.ViewHolder>() {


    override fun onCreateViewHolder(p0: ViewGroup, p1: Int): ViewHolder  {
        val view = LayoutInflater.from(p0.context).inflate(R.layout.plate_item, p0, false)

        return ViewHolder(view)
    }

    override fun onBindViewHolder(p0: ViewHolder, p1: Int) {
        val plateEntry = platesEntries[p1]

        p0.plate.text = plateEntry.plate
        p0.mDetete.setOnClickListener {
            firestoreDB.collection("plates")
                .document(plateEntry.id!!)
                .delete()
                .addOnCompleteListener {
                    platesEntries.removeAt(p1)
                    notifyItemRemoved(p1)
                    notifyItemRangeChanged(p1, platesEntries.size)
                    Toast.makeText(context, "Plate has been deleted!", Toast.LENGTH_SHORT).show()
                }
        }

    }

    override fun getItemCount(): Int {
        return platesEntries.size
    }

    inner class ViewHolder internal constructor(view: View) : RecyclerView.ViewHolder(view) {
        //internal var user: TextView
        internal var plate:TextView = view.findViewById(R.id.tvPlate)
        internal val mDetete: ImageView = view.findViewById(R.id.ivDelete)
    }

}