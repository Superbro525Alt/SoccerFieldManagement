<script lang="ts">
      import { Serialport } from "tauri-plugin-serialport-api";
      import {Button, ButtonGroup, Card} from "flowbite-svelte";
      import {ArrowRightOutline} from "flowbite-svelte-icons";
      import { exit } from '@tauri-apps/api/process';
      import { listen } from '@tauri-apps/api/event';

      interface port {
        path: string;
        baudRate: number;
        opened_port: Serialport | null;
      }
      
      let ports: port[] = [];
      let current_port: port | null = null;
      let displayed_ports: string[] = [];
      let connected: boolean = false;
      let serial_out: any = [];
      let unlisten: any;
      let _serial_out: any = {};

      let canvas;
      let terminal;


      function init_ports() {
          for (let i = 0; i < ports.length; i++) {
              if (ports[i].opened_port == null) {
                  ports[i].opened_port = new Serialport({path: ports[i].path, baudRate: ports[i].baudRate});
              }
          }
      }

      function init_port(_port: port) {
          _port.opened_port = new Serialport({path: _port.path, baudRate: _port.baudRate});

          open_port(_port);
      }

      function connect(_port: port, init: boolean = false) {
          try {
              ports.push(_port);
              if (init) {
                  init_port(_port);
              }
          } catch (e) {
                console.log(e);
          }
          return _port;
      }

      function send_data(_port: port, data: string) {
          _port.opened_port?.write(data);
      }

      function get_data(_port: port) {
          _port.opened_port?.read().then((data) => {
              console.log(data);
          });
      }

      function get_open_ports() {
          return Serialport.available_ports();
      }

      function open_port(_port: port) {
          // if port already opened
          try {
              close_port(_port.opened_port);
              _port.opened_port?.open();
          } catch (e) {
              console.log(e);
          }
      }

      function open_all_ports() {
          for (let i = 0; i < ports.length; i++) {
            open_port(ports[i]);
          }
      }

        function close_port(_port: port) {
            _port.opened_port?.close();
            current_port = null;
            connected = false;
        }

        function update_dynamic() {
            get_open_ports().then((data) => {
                displayed_ports = data;
            });
        }

        function render_field() {
            if (connected) {

                let ctx = canvas.getContext("2d");
                // draw a soccer field
                var pitch = {
                    center: {
                        lat: 0,
                        lon: 0
                    },
                    draw: function () {

                        // Outer lines
                        ctx.beginPath();
                        ctx.rect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = "#060";
                        ctx.fill();
                        ctx.lineWidth = 1;
                        ctx.strokeStyle = "#FFF";
                        ctx.stroke();
                        ctx.closePath();

                        ctx.fillStyle = "#FFF";

                        // Mid line
                        ctx.beginPath();
                        ctx.moveTo(canvas.width / 2, 0);
                        ctx.lineTo(canvas.width / 2, canvas.height);
                        ctx.stroke();
                        ctx.closePath();

                        //Mid circle
                        ctx.beginPath()
                        ctx.arc(canvas.width / 2, canvas.height / 2, 73, 0, 2 * (Math.PI), false);
                        ctx.stroke();
                        ctx.closePath();
                        //Mid point
                        ctx.beginPath()
                        ctx.arc(canvas.width / 2, canvas.height / 2, 2, 0, 2 * Math.PI, false);
                        ctx.fill();
                        ctx.closePath();

                        //Home penalty box
                        ctx.beginPath();
                        ctx.rect(0, (canvas.height - 322) / 2, 132, 322);
                        ctx.stroke();
                        ctx.closePath();
                        //Home goal box
                        ctx.beginPath();
                        ctx.rect(0, (canvas.height - 146) / 2, 44, 146);
                        ctx.stroke();
                        ctx.closePath();
                        //Home goal
                        ctx.beginPath();
                        ctx.moveTo(1, (canvas.height / 2) - 22);
                        ctx.lineTo(1, (canvas.height / 2) + 22);
                        ctx.lineWidth = 2;
                        ctx.stroke();
                        ctx.closePath();
                        ctx.lineWidth = 1;

                        //Home penalty point
                        ctx.beginPath()
                        ctx.arc(88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
                        ctx.fill();
                        ctx.closePath();
                        //Home half circle
                        ctx.beginPath()
                        ctx.arc(88, canvas.height / 2, 73, 0.29 * Math.PI, 1.71 * Math.PI, true);
                        ctx.stroke();
                        ctx.closePath();

                        //Away penalty box
                        ctx.beginPath();
                        ctx.rect(canvas.width - 132, (canvas.height - 322) / 2, 132, 322);
                        ctx.stroke();
                        ctx.closePath();
                        //Away goal box
                        ctx.beginPath();
                        ctx.rect(canvas.width - 44, (canvas.height - 146) / 2, 44, 146);
                        ctx.stroke();
                        ctx.closePath();
                        //Away goal
                        ctx.beginPath();
                        ctx.moveTo(canvas.width - 1, (canvas.height / 2) - 22);
                        ctx.lineTo(canvas.width - 1, (canvas.height / 2) + 22);
                        ctx.lineWidth = 2;
                        ctx.stroke();
                        ctx.closePath();
                        ctx.lineWidth = 1;
                        //Away penalty point
                        ctx.beginPath()
                        ctx.arc(canvas.width - 88, canvas.height / 2, 1, 0, 2 * Math.PI, true);
                        ctx.fill();
                        ctx.closePath();
                        //Away half circle
                        ctx.beginPath()
                        ctx.arc(canvas.width - 88, canvas.height / 2, 73, 0.71 * Math.PI, 1.29 * Math.PI, false);
                        ctx.stroke();
                        ctx.closePath();

                        //Home L corner
                        ctx.beginPath()
                        ctx.arc(0, 0, 8, 0, 0.5 * Math.PI, false);
                        ctx.stroke();
                        ctx.closePath();
                        //Home R corner
                        ctx.beginPath()
                        ctx.arc(0, canvas.height, 8, 0, 2 * Math.PI, true);
                        ctx.stroke();
                        ctx.closePath();
                        //Away R corner
                        ctx.beginPath()
                        ctx.arc(canvas.width, 0, 8, 0.5 * Math.PI, 1 * Math.PI, false);
                        ctx.stroke();
                        ctx.closePath();
                        //Away L corner
                        ctx.beginPath()
                        ctx.arc(canvas.width, canvas.height, 8, 1 * Math.PI, 1.5 * Math.PI, false);
                        ctx.stroke();
                        ctx.closePath();
                    }
                };

                var ball = {
                    x: 0,
                    y: 0,
                    speed: 100,
                    target: {
                        x: 0,
                        y: 0
                    },
                    move: function () {
                        let temp_data = serial_out.ball;
                        let coord = {
                            lon: temp_data[3],
                            lat: temp_data[4]
                        }

                        console.log(coord);

                        // convert the lat and lon to relative x and y positions based on the pitch center lat and lon
                        this.x = (coord.lon - pitch.center.lon) * 100;
                        this.y = (coord.lat - pitch.center.lat) * 100;

                        this.draw();
                    },
                    draw: function () {
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI, false);
                        ctx.fillStyle = "#FFF";
                        ctx.fill();
                        ctx.strokeStyle = "#000";
                        ctx.stroke();
                        ctx.closePath();
                    }
                };

                class player {
                    team;
                    id;
                    pitch;
                    x;
                    y;
                    constructor(team, id) {
                        this.team = team;
                        this.id = id;

                        this.pitch = pitch;
                    }

                    update() {
                        this.x = (serial_out.players[this.id][3] - this.pitch.center.lon) * 100;
                        this.y = (serial_out.players[this.id][4] - this.pitch.center.lat) * 100;

                        this.draw();
                    }

                    draw() {
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI, false);
                        ctx.fillStyle = ((this.team === "red") ? "#00F" : "#F00");
                        ctx.fill();
                        ctx.strokeStyle = "#000";
                        ctx.stroke();
                        ctx.closePath();
                    }

                }

                // var player = {
                //     team: "home",
                //     speed: 1.5,
                //     x: 10,
                //     y: 10,
                //     isAt: function (point) {
                //         return Math.abs(this.x - point.x) < 1 ? (Math.abs(this.y - point.y) < 1 ? true : false) : false;
                //     },
                //     move: function (point) {
                //         if (!this.isAt(point)) {
                //
                //             var h = Math.sqrt(Math.pow(Math.abs(this.x - point.x), 2) + Math.pow(Math.abs(this.y - point.y), 2));
                //             var v = Math.acos((Math.abs(this.x - point.x) / h));
                //             var x = this.speed * Math.cos(v);
                //             var y = this.speed * Math.sin(v);
                //
                //             if (point.x >= this.x && point.y >= this.y) {
                //                 this.x += x;
                //                 this.y += y;
                //             } else if (point.x >= this.x && point.y < this.y) {
                //                 this.x += x;
                //                 this.y -= y;
                //             } else if (point.x < this.x && point.y >= this.y) {
                //                 this.x -= x;
                //                 this.y += y;
                //             } else if (point.x < this.x && point.y < this.y) {
                //                 this.x -= x;
                //                 this.y -= y;
                //             }
                //             this.draw();
                //         }
                //     },
                //     draw: function () {
                //         pitch.draw();
                //         ctx.beginPath();
                //         ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI, false);
                //         ctx.fillStyle = ((this.team === "home") ? "#00F" : "#F00");
                //         ctx.fill();
                //         ctx.strokeStyle = "#000";
                //         ctx.stroke();
                //         ctx.closePath();
                //     }
                // };
                try {
                    pitch.draw();

                    let players = [];
                    for (let i = 0; i < _serial_out.players.length; i++) {
                        players[i] = new player(_serial_out.players[i][0] == "0" ? "red" : "blue", i);
                    }
                    ball.draw();
                    //player.draw();

                    for (let i = 0; i < _serial_out.players.length; i++) {
                        players[i].draw();
                    }
                } catch (e) {
                    console.log(e);
                }





            }

        }

        async function quit() {
          console.log("quit")
            // quit tauri
            await exit(0)
        }

        function update_terminal() {
            if (connected) {
                current_port.opened_port?.read();
            }
        }

        function create_serial_listener() {
          console.log("Reading...");
            unlisten = listen('plugin-serialport-read-' + current_port.path, (event) => {
                // convert array like 84,101,115,116,13,10 to Test
                let str = String.fromCharCode.apply(event.payload.data, event.payload.data);


                //strip /n and /r
                str = str.replace(/(\r\n|\n|\r)/gm, "");


                if (str.split()[0] == "0" || str.split()[0] == "1") {
                    _serial_out.players[str.split()[1]] = str.split();
                } else {
                    _serial_out.ball = str.split();
                }
                serial_out += str + " ";

                console.log(serial_out)
                terminal.scrollTop = terminal.scrollHeight;


            });
        }



        update_dynamic();

        //render_field();


</script>
{#if !connected}
<div class="full-width flex flex-col items-center justify-center">
    <ButtonGroup class="full-width mt-5">
        <Button on:click={update_dynamic}>Update</Button>
        <Button on:click={quit}>Quit</Button>
    </ButtonGroup>
    {#if displayed_ports.length != 0}
{#each displayed_ports as port}
    <div class="w-1/2 center-margin">
    <Card href="/" size="xl" padding="xl" class="min-w-max mb-5 mt-3">
          <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">Available Connection</h5>
    <p class="mb-3 font-normal text-gray-700 dark:text-gray-400 leading-tight">Port: {port}</p>

        <Button class="w-fit" on:click={() => {current_port = connect({path: port, baudRate: 9600   , opened_port: null}, true); connected=true; setTimeout(() => {create_serial_listener();render_field();update_terminal();}, 1000);}}>
            Read Serial <ArrowRightOutline class="w-3.5 h-3.5 ml-2 text-white" />
        </Button>
    </Card>
    </div>

{/each}
        {/if}
    {#if displayed_ports.length == 0}
        <div class="w-1/2 center-margin">
            <Card href="/" size="xl" padding="xl" class="min-w-max mb-5 mt-3">
                <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">No available connections (loading...)</h5>
            </Card>
        </div>
    {/if}
</div>
{/if}

{#if connected}

    <div class="w-[calc(100%-2rem)] center-margin">
    <h1 class="full-width center-margin text-center">Current connected port: {current_port.path}</h1>

        <br/>
        <canvas bind:this={canvas} class="canvas center-margin" width="800" height="518">

        </canvas>
        <br/>

        <!-- create a terminal -->
        <div bind:this={terminal} class="terminal center-margin">
            {serial_out}
        </div>

        <br/>



    <ButtonGroup divClass="full-width" size="xl">
        <Button on:click={close_port(current_port)} class="full-width" >Disconnect</Button>
    </ButtonGroup>

    </div>
{/if}

<style>
    .full-width {
        width: 100%;
        min-width: 100%;
    }

    .center-margin {
        margin-left: auto;
        margin-right: auto;
    }

    canvas {
        border: solid 10px #060;
    }

    .terminal {

        background-color: #000;
        color: #FFF;
        height: 200px;
        overflow-y: scroll;
    }
</style>
