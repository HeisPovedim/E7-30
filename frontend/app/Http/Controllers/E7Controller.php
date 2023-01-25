<?php

namespace App\Http\Controllers;

use App\Models\E7;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

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

  public function getData(Request $request){
      dump('попал в контроллер');
      $checkbox = null;
      if(is_null($request->input('z_only'))){
        $checkbox = false;
      }else{
        $checkbox = true;
      }
      $parametrs = [
        'f_start' => $request->input('f_start'),
        'f_end' => $request->input('f_end'),
        'step' => $request->input('step'),
        'z_only' => $checkbox,
      ];
;
   $response =  Http::post('http://127.0.0.1:3456/start',$parametrs);
   $data = json_decode($response->body());


    $tmpSplitData = [];
   foreach ($data as $el){
    dump($el);
    $myValues = explode(',', $el);
    array_push($tmpSplitData,$myValues);
   }
   dump('end result');
   //dd($tmpSplitData);
   $reverseData =[];
   for ($i=0; $i < count($tmpSplitData[0]); $i++) {
        $tmpDataReverse =[];
        for ($j=0; $j < count($tmpSplitData); $j++) { 
            array_push($tmpDataReverse,$tmpSplitData[$j][$i]);
        }
        array_push($reverseData,$tmpDataReverse);
   }
   dump('reverse:');
  // dd($reverseData);
   //dd('end pros die');
   //перебрать 
   //запись в файл
   $str = " ";
   foreach ($reverseData as $innerArr) {
    foreach ($innerArr as $item) {
        $str .= $item . ",";
    }
    $str .=  "\n";
}
   file_put_contents('data.csv', $str);
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
