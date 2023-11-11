<script lang="ts">
      import { Serialport } from "tauri-plugin-serialport-api";
      import {Button, ButtonGroup, Card, Footer, Heading} from "flowbite-svelte";
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
                serial_out = "Connected";
                    let current_sequence = "initial";
                    let next_sequence = ["kick", "defend", "goal"];

                let ctx = canvas.getContext("2d");
                // draw a soccer field
                let sequences = {
                    initial: {
                        sleep: 0,
                        ball: {
                            sleep: 3000,
                            speed: 1,
                            start: {
                                x: canvas.width / 2,
                                y: canvas.height / 2
                            },
                            end: {
                                x: canvas.width / 2,
                                y: canvas.height / 2
                            }
                        },
                        players: [
                            {
                                team: "red",
                                id: 0,
                                speed: 0.6,
                                sleep: 3000,
                                start: {
                                    x: canvas.width / 2 - 20,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 - 3,
                                    y: canvas.height / 2
                                }
                            },
                            {
                                team: "blue",
                                id: 0,
                                speed: 1,
                                sleep: 3000,
                                start: {
                                    x: canvas.width / 2 + 20,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 + 20,
                                    y: canvas.height / 2
                                }
                            }
                        ]
                    },
                    kick: {
                        sleep: 0,
                        ball: {
                            sleep: 0,
                            speed: 1,
                            start: {
                                x: canvas.width / 2,
                                y: canvas.height / 2
                            },
                            end: {
                                x: canvas.width / 2 + 70,
                                y: canvas.height / 2 + 2
                            }
                        },
                        players: [
                            {
                                team: "red",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 - 3,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 + 10,
                                    y: canvas.height / 2
                                }
                            },
                            {
                                team: "blue",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 + 20,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 + 40,
                                    y: canvas.height / 2 + 10
                                }
                            }
                        ]
                    },
                    defend: {
                        sleep: 0,
                        ball: {
                            sleep: 0,
                            speed: 2,
                            start: {
                                x: canvas.width / 2 + 70,
                                y: canvas.height / 2 + 2
                            },
                            end: {
                                x: canvas.width / 2 + 70,
                                y: canvas.height / 2 + 2
                            }
                        },
                        players: [
                            {
                                team: "red",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 + 10,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 + 70,
                                    y: canvas.height / 2 + 2
                                }
                            },
                            {
                                team: "blue",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 + 40,
                                    y: canvas.height / 2 + 10
                                },
                                end: {
                                    x: canvas.width / 2 + 40,
                                    y: canvas.height / 2 + 2
                                }
                            }
                        ]
                    },
                    goal: {
                        sleep: 0,
                        score_at_end: {
                            red: 0,
                            blue: 1
                        },
                        ball: {
                            sleep: 500,
                            speed: 2,
                            start: {
                                x: canvas.width / 2 + 70,
                                y: canvas.height / 2 + 2
                            },
                            end: {
                                x: canvas.width - 10,
                                y: canvas.height / 2 + 6
                            }
                        },
                        players: [
                            {
                                team: "red",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 + 10,
                                    y: canvas.height / 2
                                },
                                end: {
                                    x: canvas.width / 2 + 120,
                                    y: canvas.height / 2 + 10
                                }
                            },
                            {
                                team: "blue",
                                id: 0,
                                speed: 1,
                                sleep: 0,
                                start: {
                                    x: canvas.width / 2 + 40,
                                    y: canvas.height / 2 + 2
                                },
                                end: {
                                     x: canvas.width / 2 + 30,
                                    y: canvas.height / 2 + 20
                                }
                            }
                        ]
                    }
                }

                var ball = {
                    x: canvas.width / 2,
                    y: canvas.height / 2,
                    speed: 1,
                    target: {
                        x: 100,
                        y: 100
                    },
                    move: function () {
                        // move toward the target
                        if (!this.isAt(this.target)) {
                            var h = Math.sqrt(Math.pow(Math.abs(this.x - this.target.x), 2) + Math.pow(Math.abs(this.y - this.target.y), 2));
                            var v = Math.acos((Math.abs(this.x - this.target.x) / h));
                            var x = this.speed * Math.cos(v);
                            var y = this.speed * Math.sin(v);
                            if (x < 1) {
                                x = 1;
                            }
                            if (y < 1) {
                                y = 1;
                            }

                            if (this.target.x >= this.x && this.target.y >= this.y) {
                                this.x += x;
                                this.y += y;
                            } else if (this.target.x >= this.x && this.target.y < this.y) {
                                this.x += x;
                                this.y -= y;
                            } else if (this.target.x < this.x && this.target.y >= this.y) {
                                this.x -= x;
                                this.y += y;
                            } else if (this.target.x < this.x && this.target.y < this.y) {
                                this.x -= x;
                                this.y -= y;
                            }

                            console.log(this.x, this.y)

                        }
                        else {
                            console.log("Ball is at target")
                        }

                        this.draw();
                    },
                    draw: function () {
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, 5, 0, 3 * Math.PI, false);
                        ctx.fillStyle = "#ffffff";
                        ctx.fill();
                        ctx.strokeStyle = "#000";
                        ctx.stroke();
                        ctx.closePath();
                    },
                    isAt(target: { x: number; y: number }) {
                        return Math.abs(this.x - target.x) < 1 ? (Math.abs(this.y - target.y) < 1) : false;
                    },
                    loop: function () {
                        this.move();
                    }
                };
                class player {
                    team;
                    id;
                    pitch;
                    x;
                    y;

                    target: {
                        x: number;
                        y: number;
                    }
                    speed: number;

                    constructor(team, id) {
                        this.team = team;
                        this.id = id;

                        this.pitch = pitch;
                    }

                    update() {
                        // this.x = (serial_out.players[this.id][3] - this.pitch.center.lon) * 100;
                        // this.y = (serial_out.players[this.id][4] - this.pitch.center.lat) * 100;

                        this.draw();
                    }
                    move() {
                        // move toward the target
                        if (!this.isAt(this.target)) {
                            var h = Math.sqrt(Math.pow(Math.abs(this.x - this.target.x), 2) + Math.pow(Math.abs(this.y - this.target.y), 2));
                            var v = Math.acos((Math.abs(this.x - this.target.x) / h));
                            var x = this.speed * Math.cos(v);
                            var y = this.speed * Math.sin(v);
                            if (x < 1) {
                                x = 1;
                            }
                            if (y < 1) {
                                y = 1;
                            }
                            if (this.target.x >= this.x && this.target.y >= this.y) {
                                this.x += x;
                                this.y += y;
                            } else if (this.target.x >= this.x && this.target.y < this.y) {
                                this.x += x;
                                this.y -= y;
                            } else if (this.target.x < this.x && this.target.y >= this.y) {
                                this.x -= x;
                                this.y += y;
                            } else if (this.target.x < this.x && this.target.y < this.y) {
                                this.x -= x;
                                this.y -= y;
                            }

                            console.log(this.x, this.y)

                        }
                        else {
                            console.log("Ball is at target")
                        }

                        this.draw();
                    }
                    draw() {
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, 6, 0, 2 * Math.PI, false);
                        ctx.fillStyle = ((this.team === "red") ? "#00F" : "#F00");
                        ctx.fill();
                        ctx.strokeStyle = "#000";
                        ctx.stroke();
                        ctx.closePath();
                    }

                    private isAt(target: { x: number; y: number }) {
                        // find if this.x and this.y is at target
                        return Math.abs(this.x - target.x) < 0.1 ? (Math.abs(this.y - target.y) < 0.1) : false;
                    }
                }

                var pitch = {
                    players: [],
                    center: {
                        lat: 0,
                        lon: 0
                    },
                    do_draw: false,
                    sleep: 1000,
                    ball_move: false,
                    player_move: [false, false],
                    current: -1,
                    redScore: 0,
                    blueScore: 0,

                    draw: function () {
                        // draw score


                        // fill
                        ctx.beginPath();
                        ctx.rect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = "#060";
                        ctx.fill();
                        ctx.closePath();

                        // Outer lines
                        ctx.beginPath();
                        ctx.rect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = "#060";
                        ctx.fill();
                        ctx.lineWidth = 1;
                        ctx.strokeStyle = "#FFF";
                        ctx.stroke();
                        ctx.closePath();




                        if (this.do_draw) {
                            if (this.ball_move) {
                                ball.loop();
                            } else {
                                ball.draw();
                            }
                            for (let i = 0; i < this.players.length; i++) {
                                if (this.player_move[i]) {
                                    this.players[i].move();
                                } else {
                                    this.players[i].draw();
                                }
                            }
                        }
                        else {
                            ball.draw();
                            for (let i = 0; i < this.players.length; i++) {
                                this.players[i].draw();
                            }
                        }

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
                        // ctx.font = "30px Arial";
                        // ctx.fillStyle = "#9e9a9a";
                        // ctx.fillText(this.blueScore + " - " + this.redScore, canvas.width / 2 - 30, 60);
                        // show bnlue score in blue and red score in red
                        ctx.font = "30px Arial";
                        ctx.fillStyle = "#00F";
                        ctx.fillText(this.blueScore.toString(), canvas.width / 2 - 30, 60);
                        ctx.fillStyle = "#F00";
                        ctx.fillText(this.redScore.toString(), canvas.width / 2 + 13, 60);

                        this.check_for_sequence_change();

                        setTimeout(() => {this.draw()}, 10);
                    },

                    init: function () {
                        console.log(current_sequence)
                        this.sleep = sequences[current_sequence].sleep;

                        ball.x = sequences[current_sequence].ball.start.x;
                        ball.y = sequences[current_sequence].ball.start.y;

                        ball.target.x = sequences[current_sequence].ball.end.x;
                        ball.target.y = sequences[current_sequence].ball.end.y;

                        for (let i = 0; i < sequences[current_sequence].players.length; i++) {
                            this.players[i] = new player(sequences[current_sequence].players[i].team, i);
                            this.players[i].x = sequences[current_sequence].players[i].start.x;
                            this.players[i].y = sequences[current_sequence].players[i].start.y;
                            this.player_move[i] = false;

                            console.log(this.players[i])

                            this.players[i].target = {
                                x: sequences[current_sequence].players[i].end.x,
                                y: sequences[current_sequence].players[i].end.y
                            }

                            this.players[i].speed = sequences[current_sequence].players[i].speed;

                            this.ball_move = false;

                            setTimeout(() => {this.set_do_draw(true)}, this.sleep);
                            for (let i = 0; i < this.players.length; i++) {
                                setTimeout(() => {this.set_player_move(i, true)}, sequences[current_sequence].players[i].sleep);
                            }
                            setTimeout(() => {this.set_ball_move(true)}, sequences[current_sequence].ball.sleep);
                        }
                    },

                    set_do_draw: function (value: boolean) {
                        this.do_draw = value;
                    },
                    set_player_move(id: number, value: boolean) {
                        this.player_move[id] = value;
                    },
                    set_ball_move(value: boolean) {
                        this.ball_move = value;
                    },
                    check_for_sequence_change: function () {
                        if (this.ball_move) {
                            if (ball.isAt(ball.target)) {
                                for (let i = 0; i < this.players.length; i++) {
                                    if (this.players[i].isAt(this.players[i].target) && this.player_move[i]) {
                                        if (sequences[current_sequence].score_at_end != undefined) {
                                            // score
                                            this.redScore += sequences[current_sequence].score_at_end.red;
                                            this.blueScore += sequences[current_sequence].score_at_end.blue;

                                            serial_out += "<p class='goal-text'> Goal: " + this.blueScore + " - " + this.redScore + "</p>"
                                            terminal.innerHTML = serial_out;

                                            // fill
                                            ctx.beginPath();
                                            ctx.rect(0, 0, canvas.width, canvas.height);
                                            ctx.fillStyle = "#060";
                                            ctx.fill();
                                            ctx.closePath();

                                            // Outer lines
                                            ctx.beginPath();
                                            ctx.rect(0, 0, canvas.width, canvas.height);
                                            ctx.fillStyle = "#060";
                                            ctx.fill();
                                            ctx.lineWidth = 1;
                                            ctx.strokeStyle = "#FFF";
                                            ctx.stroke();
                                            ctx.closePath();


                                            if (this.do_draw) {
                                                if (this.ball_move) {
                                                    ball.loop();
                                                } else {
                                                    ball.draw();
                                                }
                                                for (let i = 0; i < this.players.length; i++) {
                                                    if (this.player_move[i]) {
                                                        this.players[i].move();
                                                    } else {
                                                        this.players[i].draw();
                                                    }
                                                }
                                            } else {
                                                ball.draw();
                                                for (let i = 0; i < this.players.length; i++) {
                                                    this.players[i].draw();
                                                }
                                            }

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
                                            ctx.font = "30px Arial";
                        ctx.fillStyle = "#00F";
                        ctx.fillText(this.blueScore.toString(), canvas.width / 2 - 30, 60);
                        ctx.fillStyle = "#F00";
ctx.fillText(this.redScore.toString(), canvas.width / 2 + 13, 60);
                                        }
                                        current_sequence = next_sequence[this.current + 1];
                                        this.current = this.current + 1;
                                        this.init();
                                    }
                                }
                            }
                        }
                    }
                };



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
                    // for (let i = 0; i < _serial_out.players.length; i++) {
                    //     players[i] = new player(_serial_out.players[i][0] == "0" ? "red" : "blue", i);
                    // }
                    pitch.init();
                    setTimeout(() => {pitch.draw();}, 0);


                    //player.draw();

                    // for (let i = 0; i < _serial_out.players.length; i++) {
                    //     players[i].draw();
                    // }






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
    <Heading class="full-width center-margin text-center">SoccerSense Live</Heading>
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
    <p class="goal-text"></p>
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
        <br/>

        <Footer class="full-width center-margin text-center">SoccerSense Live™ 2023</Footer>
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

        font-size: 30px;

        padding: 0.5%;
    }

    .goal-text {
        font-size: 30px;
        color: #FFF;
        text-align: center;
        margin-top: 20px;
    }
</style>
