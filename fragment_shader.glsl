#version 330 core
out vec4 FragColor;

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

uniform vec3 lightPos;
uniform vec3 lightColor; 
uniform sampler2D ourTexture;

uniform vec3 spotPos;
uniform vec3 spotDir;
uniform vec3 spotColor;
uniform float spotCutOff;

void main()
{
    vec4 texColor = texture(ourTexture, TexCoord);
    vec3 corObjeto = texColor.rgb * lightColor;
    
    vec3 norm = normalize(Normal);

    float ambientStrength = 0.2;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);
    
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * vec3(0.5, 0.5, 0.5);
    
    vec3 paraHolofoteDir = normalize(spotPos - FragPos);
    float theta = dot(paraHolofoteDir, normalize(-spotDir));
    
    vec3 spotlightDifusa = vec3(0.0);
    
    if(theta > spotCutOff)
    {
        float diffSpot = max(dot(norm, paraHolofoteDir), 0.0);
        float intensidade = clamp((theta - spotCutOff) / (1.0 - spotCutOff), 0.0, 1.0);
        
        float distancia = length(spotPos - FragPos);
        float atenuacao = 1.0 / (1.0 + 0.09 * distancia + 0.032 * (distancia * distancia));
        
        spotlightDifusa = diffSpot * spotColor * intensidade * atenuacao * 3.5;
    }
    
    vec3 result = (ambient + diffuse + spotlightDifusa) * corObjeto;
    FragColor = vec4(result, texColor.a);
}