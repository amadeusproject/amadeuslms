var button_counter = 0
class Button{
    constructor(config){

    }
    static validData(config,this_config){
        this.create(Button.validData(config)).draw();
    }
    create(config){
        var a = this;
        this.config = config;

        return this;
    }
    draw(){
        var a = this;

        return this;
    }
    remove(){
        var a = this;

        return this;
    }
    redraw(config){
        this.config = Button.validData(config,this.config);
        this.draw();
        return this;
    }
}