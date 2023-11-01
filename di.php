<?php

$method = $_SERVER['REQUEST_METHOD'];

if($method == 'POST'){

    $requestBody = file_get_contents('php://input');
    $json = json_decode($requestBody);

    $speech = shell_exec("python3 dinnerdata.py");

    $response = new \stdClass();
    //$response->responseId = $json->responseId;
    /*$response->speech = $speech;
    $response->displayText = $speech;
    $response->source = "diphp-webhook";
    /*$response->queryResult->queryText = $text;
    $response->queryResult->action = "input.General";
    $response->queryResult->parameters = "";
    $response->queryResult->allRequiredParamsPresent = true;
    $response->queryResult->fulfillmentText = $speech;
    $response->queryResult->fulfillmentMessages->text->text = $speech;*/
    
    /*$response->payload->google->expectUserResponse = false;
    $response->payload->google->richResponse->items[0]->simpleResponse->textToSpeech = $speech;*/
    $response->fulfillmentMessages[0]->text->text[0] = $speech;
    $response->payload->google->expectUserResponse = false;
    $response->payload->google->richResponse->items[0]->simpleResponse->textToSpeech = $speech;
    $r = json_encode($response);
    //$r.headers['Content-Type'] = 'application/json';
    echo $r;    

    
}
else
{

    echo "Method not allowed";

}
