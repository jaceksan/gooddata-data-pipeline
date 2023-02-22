window.AFRAME.registerState({
    // Initial state of our application. We have the current environment and the active menu.
    initialState: {
        executionData: [],
        xAxisTitle: "",
        xAxisTicks: [],
        yAxisTitle: "",
        yAxisTicks: [],
        zAxisTitle: "",
        zAxisTicks: [],
    },
    handlers: {
        replaceExecutionData: (state, action) => {
            state.executionData.splice(0, state.executionData.length);
            state.executionData.push(...action);
        },
        setAxes: (state, action) => {
            state.xAxisTicks.splice(0, state.xAxisTicks.length);
            state.xAxisTicks.push(...action.xAxis.ticks);
            state.xAxisTitle = action.xAxis.title;

            state.yAxisTicks.splice(0, state.yAxisTicks.length);
            state.yAxisTicks.push(...action.yAxis.ticks);
            state.yAxisTitle = action.yAxis.title;

            state.zAxisTicks.splice(0, state.zAxisTicks.length);
            state.zAxisTicks.push(...action.zAxis.ticks);
            state.zAxisTitle = action.zAxis.title;
        },
    },
    computeState: function (newState, payload) {
        newState.xAxisTitleRich = `value: ${newState.xAxisTitle}; width: 3; align: center; side: double; color: black`;
        newState.yAxisTitleRich = `value: ${newState.yAxisTitle}; width: 3; align: center; side: double; color: black`;
        newState.zAxisTitleRich = `value: ${newState.zAxisTitle}; width: 3; align: center; side: double; color: black`;
    },
});
