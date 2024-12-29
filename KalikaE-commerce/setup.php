<?php
// Get the cXML input (from the buyer's procurement system)
$input = file_get_contents('php://input');

// Load cXML request into SimpleXMLElement for parsing
$cxml = new SimpleXMLElement($input);

// Parse important data from the PunchOutSetupRequest
$buyerCookie = (string)$cxml->Request->PunchOutSetupRequest->BuyerCookie;
$operation = (string)$cxml->Request->PunchOutSetupRequest->Operation;

// Log or validate the request data (optional)
file_put_contents('punchout_log.txt', "BuyerCookie: $buyerCookie\nOperation: $operation\n", FILE_APPEND);

// Define PunchOut URL where the buyer will be redirected to complete shopping
$punchoutUrl = "https://https://lemonchiffon-ram-961910.hostingersite.com?session=$buyerCookie";

// Send PunchOutSetupResponse (XML response)
header('Content-Type: application/xml');
echo '<?xml version="1.0" encoding="UTF-8"?>';
?>
<cXML payloadID="<?= uniqid(); ?>" timestamp="<?= date('Y-m-d\TH:i:sP'); ?>" version="1.2.010">
    <Response>
        <PunchOutSetupResponse>
            <StartPage>
                <URL><?= $punchoutUrl; ?></URL>
            </StartPage>
        </PunchOutSetupResponse>
    </Response>
</cXML>
