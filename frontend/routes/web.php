<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\E7Controller;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| contains the "web" middleware group. Now create something great!
|
*/


//!E7-30 

Route::match(['get', 'post'],'/',[E7Controller::class,'main']);
Route::match(['get','post'],'/getData',[E7Controller::class,'getData']);


//E7-30. Конец
