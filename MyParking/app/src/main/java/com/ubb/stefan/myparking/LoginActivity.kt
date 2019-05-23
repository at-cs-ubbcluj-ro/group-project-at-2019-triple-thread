package com.ubb.stefan.myparking


import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import com.google.android.gms.common.SignInButton
import android.content.Intent
import android.support.design.widget.Snackbar
import android.util.Log
import android.view.View
import android.widget.Toast
import com.ubb.stefan.myparking.R.layout.activity_login
import com.google.android.gms.auth.api.Auth
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import com.google.android.gms.common.api.ApiException
import com.google.android.gms.auth.api.signin.GoogleSignInAccount
import com.google.android.gms.common.ConnectionResult
import com.google.android.gms.common.api.GoogleApiClient
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.auth.GoogleAuthProvider
import kotlinx.android.synthetic.main.activity_login.*
import java.lang.RuntimeException


class LoginActivity : AppCompatActivity(), View.OnClickListener, GoogleApiClient.OnConnectionFailedListener {

    private val TAG = "JSAGoogleSignIn"
    private val REQUEST_CODE_SIGN_IN = 1234
    private val WEB_CLIENT_ID = "223639823866-59ibcr9smsee932orgmh2cgdq4dq4lg7.apps.googleusercontent.com"

    private lateinit var mAuth: FirebaseAuth
    private lateinit var gso: GoogleSignInOptions
    private var mGoogleApiClient: GoogleApiClient? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)


        sign_in_button.setOnClickListener(this)
        //btn_sign_out.setOnClickListener(this)
        //btn_disconnect.setOnClickListener(this)

        gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(WEB_CLIENT_ID)
            .requestEmail()
            .build()


        mGoogleApiClient = GoogleApiClient.Builder(this)
            .enableAutoManage(this /* FragmentActivity */, this /* OnConnectionFailedListener */)
            .addApi(Auth.GOOGLE_SIGN_IN_API, gso)
            .build()

        mAuth = FirebaseAuth.getInstance()
    }

    override fun onStart() {
        super.onStart()

        // Check if user is signed in (non-null) and update UI accordingly.
        val currentUser = mAuth!!.currentUser
        updateUI(currentUser)
    }

    override fun onClick(v: View?) {
        val i = v!!.id

        when (i) {
            R.id.sign_in_button -> signIn()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        // Result returned from launching the Intent from GoogleSignInApi.getSignInIntent();
        if (requestCode == REQUEST_CODE_SIGN_IN) {
            val result = Auth.GoogleSignInApi.getSignInResultFromIntent(data)
            if (result.isSuccess) {
                // successful -> authenticate with Firebase
                val account = result.signInAccount
                firebaseAuthWithGoogle(account!!)
            } else {
                // failed -> update UI
                updateUI(null)
                Toast.makeText(applicationContext, "SignIn: failed!",
                    Toast.LENGTH_SHORT).show()
            }
        }

    }

    private fun firebaseAuthWithGoogle(acct: GoogleSignInAccount) {
        Log.e(TAG, "firebaseAuthWithGoogle():" + acct.id!!)

        val credential = GoogleAuthProvider.getCredential(acct.idToken, null)
        mAuth!!.signInWithCredential(credential)
            .addOnCompleteListener(this) { task ->
                if (task.isSuccessful) {
                    // Sign in success
                    Log.e(TAG, "signInWithCredential: Success!")
                    val user = mAuth!!.currentUser
                    updateUI(user)
                } else {
                    // Sign in fails
                    Log.w(TAG, "signInWithCredential: Failed!", task.exception)
                    Toast.makeText(applicationContext, "Authentication failed!",
                        Toast.LENGTH_SHORT).show()
                    updateUI(null)
                }
            }
    }

    override fun onConnectionFailed(connectionResult: ConnectionResult) {
        Log.e(TAG, "onConnectionFailed():" + connectionResult);
        Toast.makeText(applicationContext, "Google Play Services error.", Toast.LENGTH_SHORT).show();
    }

    private fun signIn() {
        val mGoogleSignInClient = GoogleSignIn.getClient(this, gso)
        val signInIntent = mGoogleSignInClient.signInIntent
        startActivityForResult(signInIntent, REQUEST_CODE_SIGN_IN)
    }

    private fun signOut() {
        // sign out Firebase
        mAuth!!.signOut()

        // sign out Google
        Auth.GoogleSignInApi.signOut(mGoogleApiClient).setResultCallback { updateUI(null) }
    }

    private fun revokeAccess() {
        // sign out Firebase
        mAuth!!.signOut()

        // revoke access Google
        Auth.GoogleSignInApi.revokeAccess(mGoogleApiClient).setResultCallback { updateUI(null) }
    }

    private fun updateUI(user: FirebaseUser?) {
        if (user != null) {
            val intent = Intent(this, MainActivity::class.java)
            intent.putExtra("email", user.email)
            intent.putExtra("uid", user.uid)
            startActivity(intent)
        } else {

        }
    }
}
