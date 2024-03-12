const bargraph = document.querySelector("#bargraph").getContext("2d");
const gradientBg = bargraph.createLinearGradient(0, 0, 0, 350);

const bFail = document.getElementById("B-failure");
const iFail = document.getElementById("I-failure");
const ibFail = document.getElementById("IB-failure");
const ioFail = document.getElementById("IO-failure");
const normal = document.getElementById("Normal");
const oFail = document.getElementById("O-failure");
const obFail = document.getElementById("OB-failure");

gradientBg.addColorStop(0, "blue");
gradientBg.addColorStop(1, "rgb(100, 0, 255)");
console.log((parseFloat(record.fields.predictions[0]) * 1000 / 1000) *
100,)
const data = [
  {
    name: "Ball Failure",
    ratio:
      (parseFloat(record.fields.predictions[0]) * 1000 / 1000) *
      100,
  },
  {
    name: "Inner Failure",
    ratio:
       (parseFloat(record.fields.predictions[1]) * 1000 / 1000) *
      100,
  },
  {
    name: "Inner Ball Wear",
    ratio:
       (parseFloat(record.fields.predictions[2]) * 1000 / 1000) *
      100,
  },
  {
    name: "Inner Outer Failure",
    ratio:
       (parseFloat(record.fields.predictions[3]) * 1000 / 1000) *
      100,
  },
  {
    name: "Normal",
    ratio:
       (parseFloat(record.fields.predictions[4]) * 1000 / 1000) *
      100,
  },
  {
    name: "Outer Failuer",
    ratio:
       (parseFloat(record.fields.predictions[5]) * 1000 / 1000) *
      100,
  },
  {
    name: "Outer Ball Failuer",
    ratio:
       (parseFloat(record.fields.predictions[6]) * 1000 / 1000) *
      100,
  },
];

bFail.innerText =data[0].ratio.toString() + "%";
iFail.innerText = data[1].ratio.toString() + "%";
ibFail.innerText = data[2].ratio.toString() + "%";
ioFail.innerText = data[3].ratio.toString() + "%";
normal.innerText = data[4].ratio.toString() + "%";
oFail.innerText = data[5].ratio.toString() + "%";
obFail.innerText = data[6].ratio.toString() + "%";

(async function () {
  new Chart(bargraph, {
    type: "bar",
    data: {
      labels: data.map((row) => row.name),
      datasets: [
        {
          data: data.map((row) => row.ratio),
          // backgroundColor: ['rgb(13, 66, 241)','rgb(13, 66, 241)','rgb(13, 66, 241)','rgb(13, 66, 241)','rgb(13, 66, 241)'],
          backgroundColor: [
            "#ffc154",
            "orangered",
            "#47b39c",
            "#4F3F70",
            "#35b951",
            "#4f3f70",
            "#000000"
          ],
          barThickness: 100,
          borderRadius: 10,
          borderWidth: 5,
          color: "white",
        },
      ],
    },
    options: {
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });
})();

const doughnut = document.querySelector("#doughnutgraph").getContext("2d");

new Chart(doughnut, {
  type: "doughnut",
  doughnutCoefficient: 0.1,
  data: {
    datasets: [
      {
        lables: data.map((row) => row.name),
        data: data.map((row) => row.ratio),
        tickLength: 12,
        backgroundColor: [
          "#ffc154",
          "orangered",
          "#47b39c",
          "#4F3F70",
          "#1F75FE",
        ],
        borderColor: ["#fc255", "#e6b56", "#47b39c", "#43F70", "#1F75FE"],
      },
    ],
  },
});
