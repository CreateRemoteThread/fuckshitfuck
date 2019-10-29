#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>

IPAddress local_IP(192,168,1,1);
IPAddress gateway(192,168,1,1);
IPAddress subnet(255,255,255,0);

ESP8266WebServer server(80);

#define PIN_WREN 1
#define PIN_CLK 0
#define PIN_DATA 2

String readStringz = "Usage: /configure?io=850&clk=20000";
int reconfigureIOEdge = 720;
int reconfigureCLKEdge = 13255;

void handleRoot()
{
  server.send(200,"text/plain",readStringz);  
}

void handleConfigure()
{
  int i = 0;
  String outMsg = "<html><pre>";
  for(i = 0;i < server.args();i++)
  {
    if(server.argName(i) == "io")
    {
      reconfigureIOEdge = atoi(server.arg(i).c_str());
      outMsg += "IO:" + server.arg(i) + "\n";
    }
    else if(server.argName(i) == "clk")
    {
      reconfigureCLKEdge = atoi(server.arg(i).c_str());
      outMsg += "CLK:" + server.arg(i) + "\n";
    }
  }
  outMsg += "</pre></html>";
  server.send(200,"text/html",outMsg); 
}

void pulseHigh()
{
  digitalWrite(PIN_CLK,0);
  digitalWrite(PIN_DATA,1);
  delay(20);
  digitalWrite(PIN_CLK,1);
  delay(20);
}

void pulseLow()
{
  digitalWrite(PIN_CLK,0);
  digitalWrite(PIN_DATA,0);
  delay(20);
  digitalWrite(PIN_CLK,1);
  delay(20);
}

void handleProgram()
{
  int i = 0;
  server.send(200,"text/plain","programming!");
  pulseHigh(); // to avoid multi driving a net.
  digitalWrite(PIN_WREN,1);
  pulseHigh();
  int internal_reconfigureIOEdge = reconfigureIOEdge;
  for(i = 0;i < 32; i++)
  {
    if(internal_reconfigureIOEdge % 2 == 0)
    {
      pulseLow();
    }
    else
    {
      pulseHigh();
    }
    internal_reconfigureIOEdge = internal_reconfigureIOEdge >> 1;
  }
  digitalWrite(PIN_WREN,0);
  delay(250);

  int internal_reconfigureCLKEdge = reconfigureCLKEdge;
  pulseHigh();
  digitalWrite(PIN_WREN,1);
  pulseLow();
  for(i = 0;i < 32; i++)
  {
    if(internal_reconfigureCLKEdge % 2 == 0)
    {
      pulseLow();
    }
    else
    {
      pulseHigh();
    }
    internal_reconfigureCLKEdge = internal_reconfigureCLKEdge >> 1;
  }
  digitalWrite(PIN_WREN,0);
}

void handleNotFound()
{
  server.send(200,"text/plain","page not found");  
}

void setup()
{
  // 3-wire bit-bang interface.
  pinMode(PIN_WREN,OUTPUT);
  pinMode(PIN_CLK,OUTPUT);
  pinMode(PIN_DATA,OUTPUT);
  WiFi.softAPConfig(local_IP, gateway, subnet);
  WiFi.softAP("FPGA Config.","TESTPASSWORDWHATEVER");
  WiFi.softAPIP();
  
  server.on("/", handleRoot);
  server.on("/configure", handleConfigure);
  server.on("/program", handleProgram);
  server.onNotFound(handleNotFound);
  server.begin();
}

void loop()
{
  server.handleClient();
}
