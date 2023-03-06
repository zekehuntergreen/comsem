const functions = require('../assessment.html')

test('checks next problem disabled', ()=>{
    functions.goToNextProb();
    expect($("#next")).toBeDisabled();
})