const bargraph = document.querySelector("#bargraph").getContext("2d");
const gradientBg = bargraph.createLinearGradient(0, 0, 0, 350);

const noFail = document.getElementById("no-failure");
const powerFail = document.getElementById("power-failure");
const heatFail = document.getElementById("heat-dissipation");
const toolFail = document.getElementById("tool-wear");
const strainFail = document.getElementById("overstrain-failure");

gradientBg.addColorStop(0, "blue");
gradientBg.addColorStop(1, "rgb(100, 0, 255)");
const data = [
  {
    name: "No Failure",
    ratio:
      (parseFloat(record.fields.predictions[0][0]) * 1000 / 1000) *
      100,
  },
  {
    name: "Power Failure",
    ratio:
       (parseFloat(record.fields.predictions[0][1]) * 1000 / 1000) *
      100,
  },
  {
    name: "Tool Wear",
    ratio:
       (parseFloat(record.fields.predictions[0][2]) * 1000 / 1000) *
      100,
  },
  {
    name: "OverStrain Failure",
    ratio:
       (parseFloat(record.fields.predictions[0][3]) * 1000 / 1000) *
      100,
  },
  {
    name: "Heat Dissipation",
    ratio:
       (parseFloat(record.fields.predictions[0][4]) * 1000 / 1000) *
      100,
  },
];

noFail.innerText = data[0].ratio.toString().slice(0,4) + "%";
powerFail.innerText = data[1].ratio.toString().slice(0,4) + "%";
toolFail.innerText = data[2].ratio.toString().slice(0,4) + "%";
strainFail.innerText = data[3].ratio.toString().slice(0,4) + "%";
heatFail.innerText = data[4].ratio.toString().slice(0,4) + "%";

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
            "#1F75FE",
          ],
          barThickness: 120,
          borderRadius: 10,
          borderWidth: 2,
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
