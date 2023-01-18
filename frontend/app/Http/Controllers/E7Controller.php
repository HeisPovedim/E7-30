<?php

namespace App\Http\Controllers;

use App\Models\E7;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Session;

class E7Controller extends Controller
{
    /**
     * Display a listing of the resource.
     *
     * @return \Illuminate\Http\Response
     */
    public function main(){
        return(view('welcome'));  
  }

  public function getData(){

   // dump('попал в контроллер');
     $respone =  Http::get('http://127.0.0.1:3456/start');
     $data = $respone->body();
     $data = $data.trim(' ');
    Session::flash('data', $data); 
    return redirect('/');
    //return(view('welcome',['data'=>$keywords]));
  }

    /**
     * Store a newly created resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return \Illuminate\Http\Response
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     *
     * @param  \App\Models\E7  $e7
     * @return \Illuminate\Http\Response
     */
    public function show(E7 $e7)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     *
     * @param  \App\Models\E7  $e7
     * @return \Illuminate\Http\Response
     */
    public function edit(E7 $e7)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \App\Models\E7  $e7
     * @return \Illuminate\Http\Response
     */
    public function update(Request $request, E7 $e7)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     *
     * @param  \App\Models\E7  $e7
     * @return \Illuminate\Http\Response
     */
    public function destroy(E7 $e7)
    {
        //
    }
}
